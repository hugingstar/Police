#!/bin/bash

# 1. 변수 설정
NAMESPACE="web"
SECRET_NAME="kojel-tls-secret"
CERT_FILE="kojel.crt"
KEY_FILE="kojel.key"

echo " 1. SSL 인증서 및 개인키 생성을 시작합니다."

# 2. OpenSSL로 인증서 생성
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout $KEY_FILE -out $CERT_FILE \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=Kojel/CN=www.kojel.com"

if [ $? -eq 0 ]; then
    echo " 인증서 파일 생성 완료: $CERT_FILE, $KEY_FILE"
else
    echo " 인증서 생성 실패"
    exit 1
fi

echo " 2. 쿠버네티스 Secret 생성을 시작합니다 (Namespace: $NAMESPACE)"

# 3. 기존에 동일한 이름의 Secret이 있으면 삭제 (중복 방지)
kubectl delete secret $SECRET_NAME -n $NAMESPACE --ignore-not-found

# 4. Secret 생성
kubectl create secret tls $SECRET_NAME \
  --cert=$CERT_FILE \
  --key=$KEY_FILE \
  -n $NAMESPACE

if [ $? -eq 0 ]; then
    echo " '$SECRET_NAME'이(가) 정상적으로 생성되었습니다."
else
    echo " Secret 생성 실패. Namespace '$NAMESPACE'가 존재하는지 확인하세요."
    exit 1
fi

# 5. 생성된 결과 확인
kubectl get secret $SECRET_NAME -n $NAMESPACE