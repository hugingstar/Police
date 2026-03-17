#!/bin/bash

kubectl delete all -l app=web-service -n web

kubectl delete -f metallb.yaml -n metallb-system # metallb 파일도 있다면 포함

kubectl get all -n web

echo "웹 서비스가 모두 내려갔습니다."