import os
import time
import schedule
from kafka import KafkaProducer

# 설정
BOOTSTRAP_SERVERS = ['10.15.0.170:9092'] # 카프카 서버 주소 (PC2에 서버를 띄웠다고 가정)
TOPIC_NAME = 'file_transfer'
WATCH_DIR = '/root/Data'

producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)

def send_files():
    print(f"작업 시작: {time.ctime()}")
    for root, dirs, files in os.walk(WATCH_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, WATCH_DIR)
            
            with open(file_path, 'rb') as f:
                file_data = f.read()
                # 헤더에 상대 경로를 포함시켜 전송 (폴더 구조 유지용)
                producer.send(TOPIC_NAME, value=file_data, key=rel_path.encode('utf-8'))
    
    producer.flush()
    print("전송 완료.")

# 매일 밤 12시(00:00), 오전 11시 예약
schedule.every().day.at("00:00").do(send_files)
schedule.every().day.at("11:00").do(send_files)

while True:
    schedule.run_pending()
    time.sleep(60)