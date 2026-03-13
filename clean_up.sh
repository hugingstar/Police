#!/bin/bash

# /root 디렉토리로 이동
cd /root || { echo "디렉토리 이동 실패"; exit 1; }

echo "--- 특정 서비스 및 네트워크 정리 작업을 시작합니다 ---"

# (1) /root/Police/postgres_server 에서 docker compose down -v 실행
if [ -d "/root/Police/postgres_server" ]; then
    echo "[Step 1] Police PostgreSQL 서버 중지 및 볼륨 삭제 중..."
    (cd /root/Police/postgres_server && docker compose down -v)
else
    echo "[Skip] /root/Police/postgres_server 디렉토리가 존재하지 않습니다."
fi

# (2) /root/Cronjob 에서 docker-compose.yaml 및 override 파일 적용하여 down -v 실행
if [ -d "/root/Cronjob" ]; then
    echo "[Step 2] Cronjob 서비스 중지 및 볼륨 삭제 중..."
    (cd /root/Cronjob && docker compose -f docker-compose.yaml -f docker-compose.override.yaml down -v)
else
    echo "[Skip] /root/Cronjob 디렉토리가 존재하지 않습니다."
fi

# (3) 지정된 특정 네트워크만 삭제
echo "[Step 3] 트레이딩 관련 특정 네트워크 제거 중..."
networks=(
    "trade_kospi_network"
    "trade_kosdaq_network"
    "trade_nasdaq_network"
    "trade_nyse_network"
)

for net in "${networks[@]}"; do
    if [ "$(docker network ls -q -f name=^${net}$)" ]; then
        docker network rm "$net" && echo "  - $net 삭제 완료"
    else
        echo "  - $net (존재하지 않음)"
    fi
done

# (4) 잔여 파일 및 디렉토리 삭제 (Cronjob, Data, Police)
echo "[Step 4] 잔여 디렉토리(Cronjob, Data, Police) 삭제 중..."
rm -rf Cronjob Data Police

echo "--- 모든 정리 작업이 완료되었습니다 ---"
echo ""

# (5) 결과 확인 (요청 사항)
echo "[Step 5] 현재 실행 중인 컨테이너 및 네트워크 상태 확인"
echo ">> Docker 컨테이너 목록 (docker ps -a):"
docker ps -a

echo ""
echo ">> Docker 네트워크 목록 (docker network ls):"
docker network ls
```

```
# 실행권한
chmod +x clean_up.sh

# 설치(Ansible, Git)
sudo ./clean_up.sh