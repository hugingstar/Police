#!/bin/bash

echo "--- 1. PVC (PersistentVolumeClaim) 삭제 시작 ---"

# monitoring 네임스페이스
kubectl delete pvc nfs-pvc-monitoring-prometheus -n monitoring
kubectl delete pvc nfs-pvc-monitoring-kjs -n monitoring

# db 네임스페이스
kubectl delete pvc nfs-pvc-db-ohit -n db

# was 네임스페이스
kubectl delete pvc nfs-pvc-was-yslee -n was

# web 네임스페이스
kubectl delete pvc nfs-pvc-web-jjh -n web

echo "--- 2. PV (PersistentVolume) 삭제 시작 ---"

kubectl delete pv nfs-pv-monitoring-prometheus
kubectl delete pv nfs-pv-monitoring-kjs
kubectl delete pv nfs-pv-db-ohit
kubectl delete pv nfs-pv-was-yslee
kubectl delete pv nfs-pv-web-jjh

echo "--- 모든 삭제 작업이 완료되었습니다. ---"