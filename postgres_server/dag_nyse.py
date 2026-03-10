from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import psycopg2
from psycopg2 import extras
import os

# --- 설정 및 환경 변수 ---
# 실제 환경에 맞게 수정하거나 Airflow Connections/Variables를 사용하는 권장합니다.
DB_CONFIG = {
    "host": "postgres_nyse_trade",
    "port": 5432,
    "user": "root",
    "password": "@419lab@",
    "database": "trade"
}

# CSV 파일이 위치한 기본 경로 (절대 경로 권장)
BASE_MARKET_PATH = "/opt/airflow/data/market" 

def fetch_and_upsert(market, execution_date, **kwargs):
    """
    특정 마켓의 데이터를 가져와 DB에 Upsert하는 핵심 로직
    """
    table_name = market.lower()
    # 실행 날짜 기준으로 데이터 수집 (예: 어제 데이터나 오늘 데이터)
    # Airflow의 execution_date(ds)를 사용하면 재실행 시에도 해당 날짜 데이터를 유지할 수 있습니다.
    target_date = execution_date.strftime("%Y-%m-%d")
    
    # 1. 종목 리스트 로드
    csv_path = f"{BASE_MARKET_PATH}/{table_name}/stock_list.csv"
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} 파일을 찾을 수 없습니다.")
        return

    domain_ = pd.read_csv(csv_path, encoding="utf-8-sig")
    
    # 마켓별 인덱스 설정
    code_index = "Code" if market in ["KOSPI", "KOSDAQ"] else "Symbol"
    time_col = "Time_stamp"

    # 2. DB 연결
    conn = psycopg2.connect(**DB_CONFIG)
    
    try:
        for idx, row in domain_.iterrows():
            code = row[code_index]
            name = row["Name"]
            
            try:
                # 데이터 호출 (FinanceDataReader)
                search_code = f"NAVER:{code}" if market in ["KOSPI", "KOSDAQ"] else code
                full = fdr.DataReader(search_code, start=target_date, end=target_date)
                
                if full.empty:
                    continue

                # 데이터 정제
                full[code_index] = code
                full["Name"] = name
                full.index = pd.to_datetime(full.index)
                full.index.name = time_col
                full.index = full.index.normalize().strftime('%Y-%m-%d')
                
                # Upsert 준비
                data = full.replace({np.nan: None}).reset_index().astype(str)
                col_labels = data.columns.tolist()
                
                # SQL 생성
                cols_for_insert = ', '.join([f'"{col}"' for col in col_labels])
                cols_update_list = ', '.join([
                    f'"{col}" = EXCLUDED."{col}"'
                    for col in col_labels if col not in [time_col, code_index]
                ])
                
                replace_query = f"""
                INSERT INTO "{table_name}_log" ({cols_for_insert})
                VALUES %s
                ON CONFLICT ("{time_col}", "{code_index}")
                DO UPDATE SET {cols_update_list};
                """

                # 실행
                with conn.cursor() as cursor:
                    data_values = [tuple(r) for r in data.values]
                    extras.execute_values(cursor, replace_query, data_values)
                conn.commit()
                
                print(f"[{market}] {code} {name} - {len(data)} rows upserted.")

            except Exception as e:
                print(f"Error fetching {code}: {e}")
                continue

    finally:
        conn.close()

# --- DAG 정의 ---
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1), # 적절한 과거 날짜 설정
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'dag_nyse',
    default_args=default_args,
    description='Daily stock price upsert to PostgreSQL',
    schedule_interval='30 15 * * *',  # 매일 아침 8시 (Cron: Minute Hour Day Month DayOfWeek)
    catchup=False,
    tags=['finance', 'stock']
) as dag:

    # 마켓 리스트 (필요에 따라 추가/삭제)
    markets = ["KOSPI", "KOSDAQ", "NASDAQ", "NYSE"]

    for mkt in markets:
        PythonOperator(
            task_id=f'sync_{mkt.lower()}',
            python_callable=fetch_and_upsert,
            op_kwargs={'market': mkt},
            # execution_date를 함수 내부로 전달
            provide_context=True,
        )