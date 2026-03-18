#!/bin/bash

YAML_FILE="mariadb-service.yaml"
NAMESPACE="db" 

if [ ! -f "$YAML_FILE" ]; then
    echo "오류: $YAML_FILE 파일을 찾을 수 없습니다."
    exit 1
fi

kubectl apply -f $YAML_FILE -n $NAMESPACE

kubectl get po,svc,deploy -n $NAMESPACE

echo "--- 배포가 완료되었습니다 ---"