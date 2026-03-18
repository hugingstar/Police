#!/bin/bash

# 변수 설정
YAML_FILE="mariadb-service.yaml"
NAMESPACE="db" # 설계도에 별도 네임스페이스가 있다면 수정하세요

echo "--- MariaDB 인프라 배포를 시작합니다 ---"

# 1. YAML 파일 존재 여부 확인
if [ ! -f "$YAML_FILE" ]; then
    echo "오류: $YAML_FILE 파일을 찾을 수 없습니다."
    exit 1
fi

# 2. Kubectl apply 실행
echo "적용 중: $YAML_FILE..."
kubectl apply -f $YAML_FILE -n $NAMESPACE

# 3. 배포 상태 확인 (Rollout status)
echo "배포 상태 확인 중..."
kubectl rollout status statefulset/mariadb -n $NAMESPACE

# 4. 파드 리스트 출력
echo "현재 실행 중인 DB 파드:"
kubectl get po,svc,deploy -n $NAMESPACE

echo "--- 배포가 완료되었습니다 ---"