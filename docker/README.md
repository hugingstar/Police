# Docker installation automation

- Ansible 사용하여 Docker 설치 과정을 자동화한다.
- Ansible 설치 과정

```
dnf install -y epel-release

# ro9
dnf install -y ansible

# ro10
dnf install -y ansible-core

# ssh pass
dnf install -y sshpass
```

- 설치할 영역을 설정합니다.

```
vi /etc/ansible/hosts

[yslee]
10.17.0.100
```

- yaml 파일은 github를 통해서 내려 받는다.

```
git clone https://github.com/hugingstar/Police.git
```

- playbook 파일 구문을 체크한다.

```
cd ansible/docker
ansible-playbook docker_install.yaml --syntax-check
```

- playbook을 실행하여 Docker 설치 자동화 파일을 적용
- rocky 그룹에 해당하는 호스트에 일괄 적용

```
ansible-playbook docker_install.yaml -k
```

- 설치 완료 시 확인 방법

```
docker --version
```

- 작동 상태 확인 방법

```
systemctl status docker  
```