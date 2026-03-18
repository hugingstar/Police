#!/bin/bash

kubectl delete svc,deploy was-service -n was

kubectl get all -n web

echo "웹 서비스가 모두 내려갔습니다."