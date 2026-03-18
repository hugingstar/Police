#!/bin/bash

# was.yaml 실행
echo "Step 1: Deploying was.yaml..."
if [ -f "was.yaml" ]; then
    kubectl apply -f was.yaml
    if [ $? -eq 0 ]; then
        echo "Successfully applied was.yaml."
    else
        echo "Error: Failed to apply was.yaml."
        exit 1
    fi
else
    echo "Error: was.yaml file not found."
    exit 1
fi

echo "---------- was service 설정 결과 ----------"
kubectl get pod,svc,deploy -n was
echo "------------------------------------------"
echo "All deployments are completed successfully."