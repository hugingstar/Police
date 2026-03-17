#!/bin/bash

kubectl delete -f metallb.yaml -n metallb-system # metallb 파일도 있다면 포함

kubectl delete -f web.yaml -n web

kubectl delete -f config.yaml -n web

kubectl get pod,svc,deploy -n web

echo "웹 서비스가 모두 내려갔습니다."