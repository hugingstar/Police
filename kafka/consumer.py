import os
from kafka import KafkaConsumer

# 설정 값
KAFKA_SERVER = 'localhost:9092'
TOPIC_NAME = 'file-transfer'
SAVE_DIR = '/root/nfs_node/Data' # 저장할 디렉토리

if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_SERVER],
    auto_offset_reset='earliest',
    group_id='file-receiver-group',
    fetch_max_bytes=52428800,
    max_partition_fetch_bytes=52428800
)

print("파일 수신 대기 중...")

for message in consumer:
    file_name = message.key.decode('utf-8')
    file_data = message.value
    
    save_path = os.path.join(SAVE_DIR, file_name)
    with open(save_path, 'wb') as f:
        f.write(file_data)
    
    print(f"파일 저장 완료: {save_path}")