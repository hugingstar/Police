#!/bin/bash

# 1. PVC 강제 삭제 (Finalizers 제거)
echo "--- 1. PVC 강제 정리 시작 ---"
PVC_LIST=(
  "nfs-pvc-db-ohit"
  "nfs-pvc-monitoring-kjs"
  "nfs-pvc-monitoring-prometheus"
  "nfs-pvc-was-yslee"
  "nfs-pvc-web-jjh"
)

for pvc in "${PVC_LIST[@]}"; do
    echo "PVC 패치 중: $pvc"
    # default 네임스페이스에 있는 것으로 보이므로 -n default 사용 (필요시 변경)
    kubectl patch pvc $pvc -n default -p '{"metadata":{"finalizers":null}}' --type merge 2>/dev/null
    kubectl delete pvc $pvc -n default --grace-period=0 --force 2>/dev/null
done

# 2. PV 강제 삭제 (Finalizers 제거)
echo "--- 2. PV 강제 정리 시작 ---"
PV_LIST=(
  "nfs-pv-db-ohit"
  "nfs-pv-monitoring-kjs"
  "nfs-pv-monitoring-prometheus"
  "nfs-pv-was-yslee"
  "nfs-pv-web-jjh"
)

for pv in "${PV_LIST[@]}"; do
    echo "PV 패치 중: $pv"
    kubectl patch pv $pv -p '{"metadata":{"finalizers":null}}' --type merge 2>/dev/null
    kubectl delete pv $pv --grace-period=0 --force 2>/dev/null
done

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
echo "--- 모든 Terminating 리소스가 정리되었습니다. ---"