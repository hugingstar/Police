#web 서버 설치 자동화 

-ansible 설치 
```
dnf install -y epel-release
dnf install -y ansible
```

vi /etc/ansible/hosts
```
[web_servers]
10.22.0.4 ansible_user=root ansible_password=P@ssw0rd
```
- yaml 파일은 github를 통해서 내려 받는다.

```
git clone -b jjh --single-branch https://github.com/hugingstar/Police.git
```
- playbook 파일 구문을 체크

```
cd Police/web
ansible-playbook web.yaml --syntax-check
```

- playbook을 실행하여 DNS 설치 파일을 적용

```
ansible-playbook web.yaml -k

```

1. 시스템 패키지 설치 (httpd, python)
2. Python 앱 의존성 패키지 설치
3. 웹 디렉토리 생성 및 소유권 변경 (apache)
4. Apache 프록시 설정 작성
5. Apache 서비스 재시작
6. FastAPI 서버 실행 (main.py)

# Web 서비스 구성 (FastAPI)
배포 전략:
  - `replicas: 2`: 고가용성을 위해 웹 서버를 2개의 Pod으로 운영.
  - `dnsPolicy: None`: 기본 쿠버네티스 DNS 대신 **직접 구축한 DNS 서버(10.22.0.3)**를 참조하도록 설정.
이미지: 가벼운 환경 구성을 위해 `python:3.9-slim` 베이스 이미지 사용.
트러블슈팅 포인트: Deployment 작성 시 `selector`와 `template.labels`를 일치시켜 Pod 관리 로직을 완성함.

-배포
```
kubectl apply -f web-k8s-deploy.yaml
```