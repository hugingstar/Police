import os
from kafka import KafkaProducer

# 1. 설정 값
KAFKA_SERVER = '10.15.0.170:9092'
TOPIC_NAME = 'file-transfer'

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

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_SERVER],
    max_request_size=52428800, # 약 50MB
    retries=5
)

def send_csv_files():
    for label, base_dir in TARGET_DIRECTORIES.items():
        if not os.path.exists(base_dir):
            print(f"경로 없음, 건너뜁니다: {base_dir}")
            continue

        print(f"[{label}] 하위 모든 디렉토리 스캔 중: {base_dir}")
        
        # os.walk를 사용하여 하위 폴더 전체를 순회합니다.
        for root, dirs, files in os.walk(base_dir):
            for file_name in files:
                # 확장자가 .csv인 파일만 처리
                if file_name.lower().endswith('.csv'):
                    file_path = os.path.join(root, file_name)
                    
                    try:
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                        
                        # Kafka로 전송
                        # key는 중복을 피하기 위해 파일명만 쓰거나, 필요시 전체 경로를 쓸 수 있습니다.
                        producer.send(
                            TOPIC_NAME, 
                            key=file_name.encode('utf-8'), 
                            value=file_data,
                            headers=[('label', label.encode('utf-8'))]
                        )
                        
                        # 출력 시 어떤 하위 경로에서 찾았는지 표시
                        relative_path = os.path.relpath(file_path, base_dir)
                        print(f"전송 완료: [{label}] {relative_path} ({len(file_data)} bytes)")
                        
                    except Exception as e:
                        print(f"전송 실패: {file_path}, 에러: {e}")

    producer.flush()
    print("모든 CSV 파일 전송 프로세스가 완료되었습니다.")

if __name__ == "__main__":
    send_csv_files()