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
- playbook 파일 구문을 체크

```
cd Police/mail
ansible-playbook mail_set.yaml --syntax-check
```

- playbook을 실행하여 DNS 설치 파일을 적용

```
ansible-playbook mail_set.yaml -k

```

1. DNS 설정
2. 메일 패키지 설치
3. Sendmail 설정 업데이트
4. Dovecot 설정
5. 서비스 시작 및 활성화