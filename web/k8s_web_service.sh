#!/bin/bash

#1. ConfigMap
echo "Step 1: Deploying config.yaml..."
if [ -f "config.yaml" ]; then
    kubectl apply -f config.yaml
    if [ $? -eq 0 ]; then
        echo "Successfully applied config.yaml."
    else
        echo "Error: Failed to apply config.yaml."
        exit 1
    fi
else
    echo "Error: config.yaml file not found."
    exit 1
fi

echo "------------------------------------"

# 2. web.yaml 실행
echo "Step 2: Deploying web.yaml..."
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

# 3. metallb.yaml 실행
echo "Step 3: Deploying metallb.yaml..."
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
kubectl get pod,svc,deploy -n web