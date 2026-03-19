import os
import json
import base64
from kafka import KafkaConsumer

# 설정
BOOTSTRAP_SERVERS = ['localhost:9092']
TOPIC_NAME = 'market_data_sync'
TARGET_BASE_DIR = '/root/nfs_node/Data' # PC2의 저장 기준점

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='market_sync_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    max_partition_fetch_bytes=10485760
)

def receive_market_files():
    print("Consumer started. Monitoring market data...")
    for message in consumer:
        val = message.value
        rel_path = val['rel_path'] # KOSPI/B1Sheet/2026-01-02/test.csv
        file_data = base64.b64decode(val['file_data'])
        
        # 저장할 전체 경로 (시장명 포함)
        final_path = os.path.join(TARGET_BASE_DIR, rel_path)
        
        # 하위 디렉토리(시장명/시트명/날짜폴더)를 한꺼번에 생성
        os.makedirs(os.path.dirname(final_path), exist_ok=True)
        
        with open(final_path, 'wb') as f:
            f.write(file_data)
        
        print(f"Saved to PC2: {final_path}")

if __name__ == "__main__":
    receive_market_files()