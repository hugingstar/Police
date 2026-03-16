#!/bin/bash

# 1. web.yaml 실행
echo "Step 1: Deploying web.yaml..."
if [ -f "web.yaml" ]; then
    kubectl apply -f web.yaml
    if [ $? -eq 0 ]; then
        echo "Successfully applied web.yaml."
    else
        echo "Error: Failed to apply web.yaml."
        exit 1
    fi
else
    echo "Error: web.yaml file not found."
    exit 1
fi

echo "------------------------------------"

# 2. metallb.yaml 실행
echo "Step 2: Deploying metallb.yaml..."
if [ -f "metallb.yaml" ]; then
    kubectl apply -f metallb.yaml
    if [ $? -eq 0 ]; then
        echo "Successfully applied metallb.yaml."
    else
        echo "Error: Failed to apply metallb.yaml."
        exit 1
    fi
else
    echo "Error: metallb.yaml file not found."
    exit 1
fi

echo "------------------------------------"
echo "All deployments are completed successfully."

# 현재 배포된 Pod 및 Service 상태 확인
kubectl get pods,svc,deploy -n web