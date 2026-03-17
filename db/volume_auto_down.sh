#!/bin/bash

echo "--- Kubernetes PVC & PV 삭제를 시작합니다 ---"

# 1. PVC 삭제 (네임스페이스별)
echo "[1/2] PVC 삭제 중..."

# monitoring 네임스페이스
kubectl delete pvc nfs-pvc-monitoring-prometheus -n monitoring --ignore-not-found
kubectl delete pvc nfs-pvc-monitoring-kjs -n monitoring --ignore-not-found

# was 네임스페이스
kubectl delete pvc nfs-pvc-was-yslee -n was --ignore-not-found

# web 네임스페이스
kubectl delete pvc nfs-pvc-web-jjh -n web --ignore-not-found

# default 네임스페이스 (중복 제거 및 명시적 삭제)
kubectl delete pvc nfs-pvc-monitoring-prometheus -n default --ignore-not-found
kubectl delete pvc nfs-pvc-monitoring-kjs -n default --ignore-not-found
kubectl delete pvc nfs-pvc-was-yslee -n default --ignore-not-found
kubectl delete pvc nfs-pvc-web-jjh -n default --ignore-not-found


# 2. PV 삭제 (PV는 클러스터 단위 자원이므로 네임스페이스가 없음)
echo "[2/2] PV 삭제 중..."

kubectl delete pv nfs-pv-monitoring-prometheus --ignore-not-found
kubectl delete pv nfs-pv-monitoring-kjs --ignore-not-found
kubectl delete pv nfs-pv-db-ohit --ignore-not-found
kubectl delete pv nfs-pv-was-yslee --ignore-not-found
kubectl delete pv nfs-pv-web-jjh --ignore-not-found

echo "--- 삭제 프로세스 완료 ---"

echo "--- [PVC] namespace: default ---"
kubectl get pvc -n default
echo "--- [PVC] namespace: monitoring ---"
kubectl get pvc -n monitoring
echo "--- [PVC] namespace: was ---"
kubectl get pvc -n was
echo "--- [PVC] namespace: db ---"
kubectl get pvc -n db
echo "--- [PVC] namespace: web ---"
kubectl get pvc -n web
echo "--- [PV] Persistent volume list"
kubectl get pv
echo "--- 모든 PV, PVC 리소스가 정리되었습니다. ---"