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
    for label, base_dir in TARGET_DIRECTORIES.items():
        if not os.path.exists(base_dir):
            print(f"경로 없음: {base_dir}")
            continue

        print(f"[{label}] 스캔 시작: {base_dir}")
        
        for root, dirs, files in os.walk(base_dir):
            for file_name in files:
                if file_name.lower().endswith('.csv'):
                    # 전체 경로 생성
                    file_path = os.path.join(root, file_name)
                    
                    # 핵심: base_dir 이후의 상대 경로를 추출합니다.
                    # 예: /root/Data/NASDAQ/B1Sheet/2026-01-02/test.csv 
                    # -> 결과: 2026-01-02/test.csv
                    rel_path = os.path.relpath(file_path, base_dir)
                    
                    try:
                        with open(file_path, 'rb') as f:
                            file_data = f.read()
                        
                        # 전송 시 headers에 'file_path' 정보를 추가합니다.
                        # 컨슈머는 이 정보를 보고 폴더를 생성하여 저장할 수 있습니다.
                        producer.send(
                            TOPIC_NAME, 
                            key=rel_path.encode('utf-8'), # Key에도 경로를 넣어 중복 방지
                            value=file_data,
                            headers=[
                                ('label', label.encode('utf-8')),
                                ('file_path', rel_path.encode('utf-8')) # 저장 위치 정보 전송
                            ]
                        )
                        print(f"전송 성공: [{label}] {rel_path} ({len(file_data)} bytes)")
                        
                    except Exception as e:
                        print(f"전송 실패: {rel_path}, 에러: {e}")

    producer.flush()
    print("모든 파일 전송 프로세스가 완료되었습니다.")

if __name__ == "__main__":
    send_csv_files()