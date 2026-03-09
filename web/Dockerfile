FROM python:3.9-slim

# 필요한 패키지 설치 (pip list 기반)
RUN apt-get update && apt-get install -y gcc libmariadb-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy pymysql cryptography python-multipart pandas numpy

# 소스 복사
WORKDIR /app
COPY . .

# 실행 (8000포트)
EXPOSE 8000
CMD ["python3", "main.py"]