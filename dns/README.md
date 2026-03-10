#dns서버 구축 자동화  

-ansible 설치 
```
dnf install -y epel-release
dnf install -y ansible
```

vi /etc/ansible/hosts
```
[dns_servers]
10.22.0.3 ansible_user=root ansible_password=P@ssw0rd
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
cd Police/dns
ansible-playbook dns_set.yaml --syntax-check
```

- playbook을 실행하여 DNS 설치 파일을 적용

```
ansible-playbook dns_set.yaml -K
```

- 수정 후 업데이트 
git pull origin jjh


1. 기존환경 정리 
2. bind 설치 
3. named.conf 자동 생성
4. Zone 설정 자동 추가
5. 도메인 레코드 파일(kojel.com.dns) 자동 생성
6. DNS 설정
7. 서비스 시작 및 자동 재시작 활성화
