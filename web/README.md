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
server {
    listen 80;
    server_name kojel.com www.kojel.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name kojel.com www.kojel.com;
    charset utf-8;

    ssl_certificate /etc/nginx/ssl/tls.crt;
    ssl_certificate_key /etc/nginx/ssl/tls.key;

    location / {
        root /usr/share/nginx/html;
        index login.html;
    }

    location /api {
        proxy_pass http://localhost:8000/;
    }
}
```

## k8s web deployment, service, metallb 생성 및 배포

- Service, metallb를 위한 경로로 들어가서 shell scripts를 시작

```
# 서비스 실행 자동
cd /root/jjh/Police/web

# 권한 부여
chmod +x k8s_web_service.sh

./k8s_web_service.sh
```
