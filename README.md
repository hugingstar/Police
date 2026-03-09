# Police Infrastructure

- Ansible을 활용하여 인프라 구축을 자동화한다.
- K8s를 사용하여 무중단 서비스를 구축한다
- 이어서, 초기에 패키지 설치 과정을 설명한다.

## Ansible installation
- OS 별 Ansible 설치 방법을 정리한다.
- Ansible을 설치한 후, Playbook을 적용하여 인프라 구축을 자동화한다.
- 수동 과정은 VMware ova로 빠져나와야한다.

- Ubuntu, Rocky Linux 에 설치 Ansible 방법 정리
- Master Node, Worker Node 둘 다 사용 가능하다.

### (1) Ansible 설치

- Ubuntu OS

```
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install -y ansible
```

- Rocky OS

```
dnf install -y epel-release

# ro9
dnf install -y ansible

# ro10
dnf install -y ansible-core

# ssh pass
dnf install -y sshpass
```

### (2) Ansible host 작성

- 설치할 영역을 설정합니다. 

```
# 호스트
vi /etc/ansible/hosts

```

- 영역 설정 (작업 종류, 목적에 따른 구성 가능)

```
[rocky]
192.168.0.100
192.168.0.101
```

- Well-known host 지정

```
ssh-keyscan -H 192.168.0.100 192.168.0.101 >> ~/.ssh/known_hosts
```

- Ping test

```
# 모든 호스트
ansible all -m ping -k

# 호스트 지정 rocky
ansible rocky -m ping -k
```

### (3) 깃 설치

- 호스트 PC에서 작업했던 yaml 파일을 git repository를 통해 Node에 위치시킵니다.

```
dnf install -y git
```

### (4) 호스트 IP 조회

- shell 명령어를 사용하여 ifconfig를 실행한다.
- Master Node에서 실행하여야 한다.

```
# 모든 호스트
ansible all -m shell -a "ifconfig" -k

# rocky 그룹 호스트
ansible rocky -m shell -a "ifconfig" -k
```

### (5) 유저 생성

- 모든 도메인 유저 설정
- Master Node에서 실행하여야 한다.

```
ansible all -m user -a "name=yslee" -k
```