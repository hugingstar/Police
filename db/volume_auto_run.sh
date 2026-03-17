#!/bin/bash

# YAML 파일들이 위치한 디렉토리 (현재 디렉토리 기준)
YAML_DIR="."

# 실행할 파일 리스트 (의존성을 고려하여 순서대로 배열)
# 만약 파일 내부에 PV와 PVC가 같이 있다면 순차 실행하면 됩니다.
YAML_FILES=(
    "nfs-pv-web.yaml"
    "nfs-pv-was.yaml"
    "nfs-pv-db.yaml"
    "nfs-pv-monitoring.yaml"
    "nfs-pv-monitoring-prometheus.yaml"
)

echo "----------------------------------------------------"
echo "Kubernetes NFS PV/PVC 리소스 생성을 시작합니다."
echo "----------------------------------------------------"

for FILE in "${YAML_FILES[@]}"; do
    FILE_PATH="$YAML_DIR/$FILE"

    if [ -f "$FILE_PATH" ]; then
        echo "[적용 중] $FILE..."
        kubectl delete -f "$FILE_PATH"
        
        if [ $? -eq 0 ]; then
            echo "성공: $FILE"
        else
            echo "오류: $FILE 적용 실패"
        fi
    else
        echo "경고: $FILE 파일을 찾을 수 없습니다. 건너뜁니다."
    fi
    echo "----------------------------------------------------"
done

echo "모든 작업이 완료되었습니다."
echo "현재 PV/PVC 상태 확인:"
kubectl get pv,pvc