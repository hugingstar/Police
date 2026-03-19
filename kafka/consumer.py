import os
from kafka import KafkaConsumer

# 설정 값
KAFKA_SERVER = 'localhost:9092' # 실제 서버 IP에 맞게 수정
TOPIC_NAME = 'file-transfer'

# 수신 측 저장 기본 경로 및 구조 정의
TARGET_DIRECTORIES = {
    "KOSPI_A": "/root/nfs_node/Data/KOSPI/A1Sheet",
    "KOSPI_B": "/root/nfs_node/Data/KOSPI/B1Sheet",
    "KOSDAQ_A": "/root/nfs_node/Data/KOSDAQ/A1Sheet",
    "KOSDAQ_B": "/root/nfs_node/Data/KOSDAQ/B1Sheet",
    "NASDAQ_A": "/root/nfs_node/Data/NASDAQ/A1Sheet",
    "NASDAQ_B": "/root/nfs_node/Data/NASDAQ/B1Sheet",
    "NYSE_A": "/root/nfs_node/Data/NYSE/A1Sheet",
    "NYSE_B": "/root/nfs_node/Data/NYSE/B1Sheet",
}

consumer = KafkaConsumer(
    TOPIC_NAME,
    bootstrap_servers=[KAFKA_SERVER],
    auto_offset_reset='earliest',
    group_id='file-receiver-group',
    fetch_max_bytes=52428800,
    max_partition_fetch_bytes=52428800
)

print("파일 수신 및 분류 저장 대기 중...")

for message in consumer:
    # 1. 파일 이름 추출 (Key)
    file_name = message.key.decode('utf-8')
    file_data = message.value
    
    # 2. Header에서 라벨 정보 추출
    label = None
    if message.headers:
        for header_key, header_value in message.headers:
            if header_key == 'label':
                label = header_value.decode('utf-8')
                break
    
    # 3. 저장 경로 결정
    if label and label in TARGET_DIRECTORIES:
        save_dir = TARGET_DIRECTORIES[label]
    else:
        # 라벨이 없거나 매칭되지 않는 경우 기본 폴더에 저장
        save_dir = "/root/nfs_node/Data/UNKNOWN"
    
    # 4. 디렉토리 생성 (없을 경우)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir, exist_ok=True)
    
    # 5. 파일 저장
    save_path = os.path.join(save_dir, file_name)
    try:
        with open(save_path, 'wb') as f:
            f.write(file_data)
        print(f"저장 성공 [{label}]: {save_path}")
    except Exception as e:
        print(f"저장 실패: {file_name}, 에러: {e}")