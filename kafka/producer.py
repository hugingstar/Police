import os
from kafka import KafkaProducer

# 1. 설정 값
KAFKA_SERVER = '10.15.0.170:9092'
TOPIC_NAME = 'file-transfer'

# 2. 탐색할 디렉토리 딕셔너리 (별칭: 실제경로)
TARGET_DIRECTORIES = {
    "KOSPI_A": "/root/Data/KOSPI/A1Sheet",
    "KOSPI_B": "/root/Data/KOSPI/B1Sheet",

    "KOSDAQ_A": "/root/Data/KOSDAQ/A1Sheet",
    "KOSDAQ_B": "/root/Data/KOSDAQ/B1Sheet",

    "NASDAQ_A": "/root/Data/NASDAQ/A1Sheet",
    "NASDAQ_B": "/root/Data/NASDAQ/B1Sheet",

    "NYSE_A": "/root/Data/NYSE/A1Sheet",
    "NYSE_B": "/root/Data/NYSE/B1Sheet",

}

# 프로듀서 생성 (메시지 크기 제한을 늘림 - 약 50MB)
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    max_request_size=52428800,
    retries=5
)

def send_csv_files():
    for label, dir_path in TARGET_DIRECTORIES.items():
        if not os.path.exists(dir_path):
            print(f"경로 없음, 건너뜁니다: {dir_path}")
            continue

        print(f"[{label}] 디렉토리 스캔 중: {dir_path}")
        
        for file_name in os.listdir(dir_path):
            # CSV 파일만 필터링
            if file_name.lower().endswith('.csv'):
                file_path = os.path.join(dir_path, file_name)
                
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                    
                    # 파일명을 key로, 파일 내용을 value로 전송
                    # (Consumer에서 저장할 때 구분하기 쉽게 label을 붙일 수도 있습니다)
                    producer.send(
                        TOPIC_NAME, 
                        key=file_name.encode('utf-8'), 
                        value=file_data
                    )
                    print(f"전송 완료: {file_name} ({len(file_data)} bytes)")
                except Exception as e:
                    print(f"전송 실패: {file_name}, 에러: {e}")

    # 버퍼에 남은 메시지 모두 전송
    producer.flush()
    print("모든 CSV 파일 전송 시도가 완료되었습니다.")

if __name__ == "__main__":
    send_csv_files()