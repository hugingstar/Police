#mail 서버 구축 자동화 

-ansible 설치 
```
dnf install -y epel-release
dnf install -y ansible
```

vi /etc/ansible/hosts
```
[mail_servers]
10.22.0.2 ansible_user=root ansible_password=P@ssw0rd
```

- yaml 파일은 github를 통해서 내려 받는다.
```
git clone -b jjh --single-branch https://github.com/hugingstar/Police.git
```

- SSH 호스트 키 불일치 방지 
vi /etc/ansible/ansible.cfg
```
[defaults]
host_key_checking = False
```

- playbook 파일 구문을 체크
```
cd Police/mail
ansible-playbook mail_set.yaml --syntax-check
```

- playbook을 실행하여 DNS 설치 파일을 적용
```
ansible-playbook mail_set.yaml -K
```

- 수정 후 업데이트
git pull origin jjh

1. DNS 설정
2. 메일 패키지 설치
3. Sendmail 설정 업데이트 (.mc 수정 및 .cf 생성)
4. Mail Access 권한 설정 및 DB 갱신
5.  Access DB 생성 (변경사항 있을 때만 실행)
6. Dovecot 설정 (통합 관리)
7. 서비스 시작 및 활성화