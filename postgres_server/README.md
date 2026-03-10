# Postgres DB 

- (주의) 이 과정은 Airflow가 설치된 이후의 작업입니다. 반드시 Airflow를 설치한 이후에 작업해주세요.

- Docker-compose를 사용하여 DB 서버 컨테이너들을 올린다.

- yaml, sql 파일은 github를 통해서 내려 받는다.

```
git clone -b yslee --single-branch https://github.com/hugingstar/Police.git
```

- compose 파일 실행 (백그라운드로 실행)
- docker network 실행

```
# Docker용 네트워크 생성
docker network create trade_kospi_network
docker network create trade_kosdaq_network
docker network create trade_nasdaq_network
docker network create trade_nyse_network

# 컨테이너 실행
docker compose up -d
```

- 데이터베이스 확인 방법 : 컨테이너 명을 사용해서 컨테이너 안으로 들어간다.
- psql -U를 사용해서 들어간다.

```
# kospi 컨테이너 접속
docker exec -it postgres_kospi_trade /bin/bash
# kosdaq 컨테이너 접속
docker exec -it postgres_kosdaq_trade /bin/bash
# nasdaq 컨테이너 접속
docker exec -it postgres_nasdaq_trade /bin/bash
# nyse 컨테이너 접속
docker exec -it postgres_nyse_trade /bin/bash

# trade 데이터베이스에 접속
psql -U root -d trade

# 데이터베이스 확인 
\dt

# 데이터베이스 확인
SELECT * FROM kospi_log LIMIT 1;

# postgres에서 나가기
\q

# 컨테이너에서 나오기(조용히 나오는 방법 Detach)
Ctrl + P + Q
```


- Data Collector는 ansible 스크립트를 사용하여 airflow 내에 있는 dags로 위치시킨다.

```

```