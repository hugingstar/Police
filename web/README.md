# Web server service 설정 방법 

## girhub clone


```
# 웹서버 관련
mkdir jjh
cd /root/jjh
git clone -b jjh --single-branch https://github.com/hugingstar/Police.git

# WAS 관련
mkdir yslee
cd /root/yslee
git clone -b yslee --single-branch https://github.com/hugingstar/Police.git
```

## SSL-Secret 실행 
- ssl 인증서 생성 및 Secret 생성

```
# 작업 경로
cd /root/Police/web

# ssl-secret 파일 생성 
vi ssl_secret.sh

# 파일 권한 부여
chmod +x ssl_secret.sh

# ssl-secret 생성 (기존 secret 중복 방지 포함)
./ssl_secret.sh
```

## Proxy
- default.conf에 proxy 설정
- location 부분은 컨테이너(or 파드) 안쪽의 경로를 지정해준다.

```
# 작업 위치에서 default.conf 생성하고 아래의 내용 작성

```

## k8s web deployment, service, metallb 생성 및 배포

- Service, metallb를 위한 경로로 들어가서 shell scripts를 시작

```
# 서비스 실행 자동
cd /root/jjh/Police/web

# 권한 부여
chmod +x k8s_web_service.sh
chmod +x k8s_web_down.sh

# 실행
./k8s_web_service.sh
./k8s_web_down.sh

# sh 파일만 권한 주기
find . -name "*.sh" -exec chmod +x {} +
find . -name "*.py" -exec chmod +x {} +
```

- 작동 상태 확인

```
kubectl get po,svc,deploy -n web
```

- Pod terminating 상황시 종료 방법 : force 옵션을 넣어야 한다.

```
kubectl delete -f <파일명>.yaml --force --grace-period=0
```

에러 확인
```
kubectl describe pod [안 뜨는 파드 이름] -n web
kubectl logs [안 뜨는 파드 이름] -n web
```

설정 재반영
kubectl rollout restart deployment web-service -n web
coreDNS확인
kubectl get pods -n kube-system -l k8s-app=kube-dns
