import os
import json
import base64
from kafka import KafkaProducer

# 설정
BOOTSTRAP_SERVERS = ['10.15.0.170:9092']
TOPIC_NAME = 'market_data_sync'
BASE_DIR = '/root/Data'  # 시장(KOSPI 등) 폴더들의 상위 디렉토리
MARKETS = ['KOSPI', 'KOSDAQ', 'NASDAQ', 'NYSE']
SHEETS = ['A1Sheet', 'B1Sheet']

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    max_request_size=10485760  # 10MB
)

def send_market_files():
    for market in MARKETS:
        for sheet in SHEETS:
            # /root/Data/KOSPI/A1Sheet
            target_path = os.path.join(BASE_DIR, market, sheet)
            
            if not os.path.exists(target_path):
                print(f"Path not found, skipping: {target_path}")
                continue

            # os.walk를 통해 B1Sheet 하위의 날짜 폴더(2026-01-02 등)까지 자동 탐색
            for root, dirs, files in os.walk(target_path):
                for file_name in files:
                    if file_name.endswith('.csv'):
                        full_path = os.path.join(root, file_name)
                        
                        # BASE_DIR(/root/Data) 기준의 상대 경로 추출
                        # 예: NASDAQ/B1Sheet/2026-01-02/data.csv
                        rel_path = os.path.relpath(full_path, BASE_DIR)
                        
                        try:
                            with open(full_path, 'rb') as f:
                                file_data = base64.b64encode(f.read()).decode('utf-8')
                            
                            message = {
                                'rel_path': rel_path,
                                'file_data': file_data
                            }
                            
                            producer.send(TOPIC_NAME, value=message)
                            print(f"Sent: {rel_path}")
                        except Exception as e:
                            print(f"Error sending {rel_path}: {e}")

    producer.flush()

if __name__ == "__main__":
    send_market_files()