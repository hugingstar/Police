import os
from kafka import KafkaProducer

# 설정 값
KAFKA_SERVER = '10.15.0.170:9092'
TOPIC_NAME = 'file-transfer'
WATCH_DIR = '/root/Data' # 보낼 파일이 있는 디렉토리

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    max_request_size=52428800  # 최대 전송 크기 설정 (예: 50MB)
)

def send_file(file_path):
    file_name = os.path.basename(file_path)
    with open(file_path, 'rb') as f:
        file_data = f.read()
        # 헤더에 파일명을 넣어 전송
        producer.send(TOPIC_NAME, value=file_data, key=file_name.encode('utf-8'))
    producer.flush()
    print(f"성공적으로 전송됨: {file_name}")

if __name__ == "__main__":
    for root, dirs, files in os.walk(WATCH_DIR):
        for file in files:
            full_path = os.path.join(root, file)
            send_file(full_path)
