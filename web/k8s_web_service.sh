#!/bin/bash

# metallb.yaml 실행
echo "Step 1: Deploying metallb.yaml..."
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

echo "---------- Metallb 설정 결과 ----------"
kubectl get ipaddresspool -n metallb-system
kubectl get l2advertisement -n metallb-system
echo "--------------------------------------"

# web.yaml 실행
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

echo "---------- Web service 설정 결과 ----------"
kubectl get pod,svc,deploy -n web
echo "------------------------------------------"
echo "All deployments are completed successfully."





