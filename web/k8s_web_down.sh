#!/bin/bash

kubectl delete svc,deploy web-service -n web

kubectl delete ipaddresspool,l2advertisement -n metallb-system --all

kubectl get all -n web

echo "웹 서비스가 모두 내려갔습니다."