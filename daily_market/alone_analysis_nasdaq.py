import os
import warnings
import pandas as pd
from datetime import datetime, timedelta


# 경고 무시
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings(action='ignore', category=pd.errors.PerformanceWarning)

class MakeSheet():
    def __init__(self, start, end, market_name):
        self.market_name = market_name
        self.start = start
        self.end = end
        self.file_path = f"/root/Data/{self.market_name}/A1Sheet"
        self._create_folder(self.file_path)
        self.TIME = "time_stamp" # 템플릿의 SQL 컬럼명에 맞춤

        weekday_list = pd.date_range(start=self.start, end=self.end, freq='B').strftime('%Y-%m-%d').tolist()
        
        try:
            files = [f for f in os.listdir(self.file_path) if f.endswith('.csv')]
            stock_info = {self.extract_name_part(f): self.extract_code_part(f) for f in files}
        except FileNotFoundError:
            print(f"Error: Path {self.file_path} 파일을 찾을 수 없습니다.")
            return
        
        # 반복해서 결과 출력
        for dcode in weekday_list:
            print(f"--- Processing Date: {dcode} ---")
            self.save_path = f"/root/Data/{self.market_name}/B1Sheet/{dcode}"
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

if __name__ == "__main__":
    market = 'NASDAQ'
    start_date = "2025-11-01"
    end_date = "2026-03-11"
    MakeSheet(start=start_date, end=end_date, market_name=market)

