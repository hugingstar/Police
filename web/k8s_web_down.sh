#!/bin/bash
kubectl delete -f web.yaml -n web

kubectl delete -f metallb.yaml -n web # metallb 파일도 있다면 포함

kubectl get pod,svc,deploy -n web

echo "웹 서비스가 모두 내려갔습니다."