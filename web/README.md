# Web server service 설정 방법 

## 초기 실행 
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





