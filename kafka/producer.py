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
            # if file_name.lower().endswith('.csv'):
            file_path = os.path.join(dir_path, file_name)
            
            try:
                with open(file_path, 'rb') as f:
                    file_data = f.read()
                
                # headers에 'label' 정보를 담아서 전송합니다.
                producer.send(
                    TOPIC_NAME, 
                    key=file_name.encode('utf-8'), 
                    value=file_data,
                    headers=[('label', label.encode('utf-8'))] # 라벨 추가
                )
                print(f"전송 완료: {label} -> {file_name} ({len(file_data)} bytes)")
            except Exception as e:
                print(f"전송 실패: {file_name}, 에러: {e}")

    producer.flush()
    print("모든 CSV 파일 전송 시도가 완료되었습니다.")

if __name__ == "__main__":
    send_csv_files()