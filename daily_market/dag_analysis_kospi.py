import os
import sys
import warnings
import pandas as pd
import numpy as np
import ta
import psycopg2
import time
from psycopg2 import extras
from datetime import datetime, timedelta
from scipy.signal import argrelextrema
from airflow import DAG
from airflow.operators.python import PythonOperator
import pendulum

# 경고 무시
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings(action='ignore', category=pd.errors.PerformanceWarning)

# --- 1. 데이터 취득부 (DataAcquirer) ---
class DataAcquirer:
    def __init__(self, host, port, user, password, db_name, market_name, start_date, end_date, code):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.market_name = market_name
        self.start_date = start_date
        self.end_date = end_date
        self.code = code
        self.data = pd.DataFrame()

        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=int(self.port),
                user=self.user,
                password=self.password,
                database=self.db_name
            )
            
            table_name = f"{self.market_name.lower()}_log"
            id_column = "code" if self.market_name.upper() in ["KOSPI", "KOSDAQ", "KONEX"] else "symbol"
            
            query = f"""
                SELECT "time_stamp", "open", "high", "low", "close", "volume"
                FROM {table_name}
                WHERE "time_stamp" BETWEEN %s AND %s 
                AND "{id_column}" = %s
            """
            params = (self.start_date, self.end_date, self.code)

            self.data = pd.read_sql(query, self.conn, params=params)
            self.data.drop_duplicates(keep='first', inplace=True)
            
            if not self.data.empty:
                print(f"--- [{self.code}] 데이터 추출 성공: {len(self.data)}행 ---")
        except Exception as e:
            print(f"Database Error: {e}")
        finally:
            if hasattr(self, 'conn'):
                self.conn.close()

    def output(self):
        return self.data

# --- 2. 기술 분석부 (TechnicalAnalyzer) ---
class TechnicalAnalyzer:
    def __init__(self, host, port, user, password, db_name, market_name, ref_date, end_date, name, stock_code_dict):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.market_name = market_name
        self.ref_date = ref_date
        self.end_date = end_date
        self.name = name
        self.code = stock_code_dict[name]

        self.out_path = f"/opt/airflow/data/Data/{self.market_name}/A1Sheet"
        self._create_folder(self.out_path)

        # 분석 파라미터
        self.rsi_rollback = 90
        self.up_div_price = [0.01, 0.15]
        self.up_div_rsi = [0.01, 0.15]

        try:
            self.source_data = DataAcquirer(
                host=self.host, port=self.port, user=self.user, 
                password=self.password, db_name=self.db_name,
                market_name=self.market_name, start_date=self.ref_date,
                end_date=self.end_date, code=self.code
            ).output()

            if not self.source_data.empty:
                self.data = self._incremental_update()
            else:
                self.data = None
        except Exception as e:
            print(f"[{self.name}] 분석 오류: {e}")
            self.data = None

    def _create_folder(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def _incremental_update(self):
        df = self.source_data.copy()
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype('float')
        
        processed_df = self._processing(df)
        file_path = f"{self.out_path}/{self.name}({self.code}).csv"
        processed_df.to_csv(file_path, encoding="utf-8-sig")
        return processed_df

    def _processing(self, data):
        data['close_diff_first'] = data['close'].diff()
        data["RSI"] = ta.momentum.RSIIndicator(data["close"], window=14).rsi()
        
        # Divergence 계산 (예시: Sell_Signal 컬럼이 생성되어야 MakeSheet에서 작동함)
        # 임시로 Sell_Signal 생성 (사용자 로직에 맞춰 수정 가능)
        data['Sell_Signal'] = np.where(data['RSI'] > 70, 1, 0) 
        
        bull, bear = self._divergence_rolling(data["close"], data["RSI"], self.rsi_rollback)
        data["RSI_BullDiv"] = bull
        data["RSI_BearDiv"] = bear
        
        return data

    def _divergence_rolling(self, price, rsi, lookback):
        n = len(price)
        bull_div = np.zeros(n, dtype=np.int8)
        bear_div = np.zeros(n, dtype=np.int8)
        if n < 2: return bull_div, bear_div
        trough_idx = argrelextrema(price.values, np.less, order=1)[0]
        for i in range(len(trough_idx)-1):
            a, b = trough_idx[i], trough_idx[i+1]
            if b - a <= lookback:
                p_pct = (price.iloc[b] - price.iloc[a]) / price.iloc[a]
                r_pct = (rsi.iloc[b] - rsi.iloc[a]) / rsi.iloc[a]
                if (self.up_div_price[0] <= p_pct <= self.up_div_price[1] and 
                    self.up_div_rsi[0] <= r_pct <= self.up_div_rsi[1]):
                    bull_div[b] = 1
        return bull_div, bear_div

# --- 3. 시트 생성부 (MakeSheet) ---
class MakeSheet():
    def __init__(self, start, end, market_name):
        self.market_name = market_name
        self.start = start
        self.end = end
        self.file_path = f"/opt/airflow/data/Data/{self.market_name}/A1Sheet"
        self._create_folder(self.file_path)
        self.TIME = "time_stamp" # 템플릿의 SQL 컬럼명에 맞춤

        weekday_list = pd.date_range(start=self.start, end=self.end, freq='B').strftime('%Y-%m-%d').tolist()
        
        try:
            files = [f for f in os.listdir(self.file_path) if f.endswith('.csv')]
            stock_info = {self.extract_name_part(f): self.extract_code_part(f) for f in files}
        except FileNotFoundError:
            print(f"Error: Path {self.file_path} 파일을 찾을 수 없습니다.")
            return

        for dcode in weekday_list:
            print(f"--- Processing Date: {dcode} ---")
            self.save_path = f"/opt/airflow/data/Data/{self.market_name}/B1Sheet/{dcode}"
            self._create_folder(self.save_path)

            df_sell_total, df_bull_total, df_bear_total = pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

            for name, code in stock_info.items():
                file_full_path = f"{self.file_path}/{name}({code}).csv"
                try:
                    data = pd.read_csv(file_full_path, index_col=self.TIME)
                    data.index = pd.to_datetime(data.index).strftime('%Y-%m-%d')
                    
                    target_data = data[data.index == dcode].copy()
                    if target_data.empty: continue

                    df_sell, df_bull, df_bear = self.BuySellSheet(target_data)

                    if not df_sell.empty:
                        df_sell.insert(0, "name", name)
                        df_sell_total = pd.concat([df_sell_total, df_sell])
                    if not df_bull.empty:
                        df_bull.insert(0, "name", name)
                        df_bull_total = pd.concat([df_bull_total, df_bull])
                    if not df_bear.empty:
                        df_bear.insert(0, "name", name)
                        df_bear_total = pd.concat([df_bear_total, df_bear])

                except Exception as e:
                    print(f"Error processing {name}: {e}")

            # 결과 저장
            df_sell_total.to_csv(f"{self.save_path}/df_sell.csv", encoding="utf-8-sig")
            df_bull_total.to_csv(f"{self.save_path}/df_bull.csv", encoding="utf-8-sig")
            df_bear_total.to_csv(f"{self.save_path}/df_bear.csv", encoding="utf-8-sig")

    def extract_name_part(self, filename):
        return filename.rsplit('(', 1)[0]
    
    def extract_code_part(self, filename):
        return filename.rsplit('(', 1)[1].replace(').csv', '')

    def BuySellSheet(self, data):
        return data[data["Sell_Signal"] == 1], data[data.get("RSI_BullDiv", 0) == 1], data[data.get("RSI_BearDiv", 0) == 1]

    def _create_folder(self, directory):
        os.makedirs(directory, exist_ok=True)

# --- 4. Airflow Tasks ---

def run_analysis_task(**kwargs):
    """테스크 1: 모든 종목 기술 지표 계산 및 저장"""
    market = kwargs.get('market', 'KOSPI')
    host = os.environ.get("HOST", "postgres_kospi_trade")
    port = os.environ.get("PORT", "5432")
    user = os.environ.get("USER", "root")
    password = os.environ.get("PASSWORD", "@419lab@")
    db_name = os.environ.get("DB_NAME", "trade")
    ref_date = os.environ.get("REF_DATE", "2024-01-01")
    end_date = datetime.now().strftime('%Y-%m-%d')

    BASE_MARKET_PATH = "/opt/airflow/data/market" 

    stock_list_path = f"{BASE_MARKET_PATH}/{market.lower()}/stock_list.csv"
    
    if not os.path.exists(stock_list_path):
        print(f"Error: {stock_list_path} 파일을 찾을 수 없습니다.")
        return

    df_dns = pd.read_csv(stock_list_path, encoding="utf-8-sig")
    code_col = 'code' if market.upper() in ["KOSPI", "KOSDAQ", "KONEX"] else 'symbol'
    stock_code_dict = dict(zip(df_dns['name'], df_dns[code_col]))

    for stock_name in df_dns['name']:
        TechnicalAnalyzer(
            host=host, port=port, user=user, password=password,
            db_name=db_name, market_name=market,
            ref_date=ref_date, end_date=end_date,
            name=stock_name, stock_code_dict=stock_code_dict
        )

def run_make_sheet_task(**kwargs):
    """테스크 2: 생성된 CSV들을 읽어 날짜별 시그널 요약 시트 생성"""
    market = kwargs.get('market', 'KOSPI')
    # 어제~오늘 날짜 기준으로 시트 생성 (스케줄러 실행 시점 고려)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    
    MakeSheet(start=start_date, end=end_date, market_name=market)

# --- 5. DAG 정의 ---

local_tz = pendulum.timezone("Asia/Seoul")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1, tzinfo=local_tz),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'dag_analysis_kospi',
    default_args=default_args,
    description='기술 분석 후 일자별 시그널 시트 생성',
    schedule_interval='0 21 * * 1-5',
    catchup=False,
    tags=['finance', 'analysis']
) as dag:

    # Task 1: 기술 분석 (A1Sheet 생성)
    analyze_task = PythonOperator(
        task_id='run_technical_analysis',
        python_callable=run_analysis_task,
        op_kwargs={'market': 'KOSPI'}
    )

    # Task 2: 시그널 통합 (B1Sheet 생성)
    make_sheet_task = PythonOperator(
        task_id='generate_signal_sheets',
        python_callable=run_make_sheet_task,
        op_kwargs={'market': 'KOSPI'}
    )

    # 순서 설정: 분석 완료 후 시트 생성
    analyze_task >> make_sheet_task