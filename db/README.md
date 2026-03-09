#db서버 구축 자동화  

```
vi /etc/ansible/hosts

[db_servers]
10.22.0.
```
- yaml 파일은 github를 통해서 내려 받는다.

```
git clone -b jjh --single-branch https://github.com/hugingstar/Police.git
```
- playbook 파일 구문을 체크

```
cd Police/db
ansible-playbook db.yaml --syntax-check
```

- playbook을 실행하여 DNS 설치 파일을 적용

```
ansible-playbook db.yaml -k
```
1. MariaDB 관련 패키지 설치 (mariadb-server, python3-pymysql)
2. MariaDB 서비스 시작 및 활성화
3. MariaDB 한글 인코딩 설정 (/etc/my.cnf.d/mariadb-server.cnf)
4. 설정 적용을 위한 서비스 재시작
5. MariaDB root 비밀번호 설정
6. 필요한 Python 라이브러리 설치 (pip)
7. SSH 포트 확인 및 서비스 보장
8. 배포 경로 생성 (/var/www/html)


