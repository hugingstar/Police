# Market Monitoring with Ansible and Airflow

- Ansible을 활용하여 인프라 구축을 자동화한다.
- Airflow를 사용하여 서로 다른 시간에 수행되어야 하는 테스크를 분산하여 자동화한다.

## 1. Ansible installation
- OS 별 Ansible 설치 방법을 정리한다.
- Ansible을 설치한 후, Playbook을 적용하여 인프라 구축을 자동화한다. (Ubuntu, Rocky Linux 에 설치 Ansible 방법 정리)

### (1) Ansible과 필요 패키지 설치
- 깃을 통해 호스트 PC에서 작업했던 yaml 파일을 git repository를 통해 Node에 위치시킨다.
- Rocky OS 기준 설명

```
# EPEL (Extra Packages for Enterprise Linux) 저장소 : 기업용 리눅스를 위한 추가 패키지
dnf install -y epel-release

# Ansible ro9 
dnf install -y ansible

# Ansible ro10
dnf install -y ansible-core

# ssh pass
dnf install -y sshpass

# 깃 설치
dnf install -y git
```

- Shell Script를 사용하여 자동화를 간편하게 합니다.
- 리눅스에서 `/root` 디렉토리에 `vi install_ansible.sh`를 추가하고, 아래의 내용을 넣는다. 

```
#!/bin/bash

# 1. 루트 권한 확인
if [ "$EUID" -ne 0 ]; then
  echo "오류: 이 스크립트는 sudo 또는 root 권한으로 실행해야 합니다."
  exit 1
fi

echo "--- 시스템 업데이트 및 필수 패키지 설치를 시작합니다 ---"

# 2. EPEL 저장소 설치
echo "[1/4] EPEL 저장소 활성화 중..."
dnf install -y epel-release

# 3. OS 버전 확인 및 Ansible 설치
OS_VER=$(rpm -E %rhel)
echo "감지된 RHEL 메이저 버전: $OS_VER"

if [ "$OS_VER" -eq 9 ]; then
    echo "[2/4] Rocky Linux 9용 Ansible 설치 중..."
    dnf install -y ansible
elif [ "$OS_VER" -eq 10 ]; then
    echo "[2/4] Rocky Linux 10용 Ansible-core 설치 중..."
    dnf install -y ansible-core
else
    echo "경고: 지원 범위를 벗어난 OS 버전입니다. 기본 ansible-core 설치를 시도합니다."
    dnf install -y ansible-core
fi

# 4. SSHPass 및 Git 설치
echo "[3/4] sshpass 설치 중 (비밀번호 인증용)..."
dnf install -y sshpass

echo "[4/4] git 설치 중..."
dnf install -y git

# 5. 설치 결과 확인
echo "--- 설치 완료 확인 ---"
ansible --version | head -n 1
git --version
sshpass -V | head -n 1

echo "모든 패키지가 성공적으로 설치되었습니다."
```

```
# 실행권한
chmod +x install_ansible.sh

# 설치(Ansible, Git)
sudo ./install_ansible.sh
```

### (2) Ansible host 작성 (수동)

- Ansible 설치를 완료한 후 `/etc/ansible/hosts`파일을 열어서 설치할 영역을 설정합니다. 
- IP 규모가 커지면 이 부분도 자동화하는 것을 추천한다.

```
# 호스트
vi /etc/ansible/hosts

# 가장 하단에 아래의 형식을 따라 추가한다.(IP는 각자 다를 수 있다.)
[rocky]
192.168.0.100
192.168.0.101
```

- (필요시) Well-known host 지정이 필요하다.

```
export ANSIBLE_HOST_KEY_CHECKING=False

ssh-keyscan -H 192.168.0.100 192.168.0.101 >> ~/.ssh/known_hosts
```

- Ping test

```
# 모든 호스트
ansible all -m ping -k

# 호스트 지정 rocky
ansible rocky -m ping -k
```

### (3) 호스트 IP 조회

- Ansible Shell 명령어를 사용하여 연결 상태를 확인한다.
- 이 과정에서 연결이 안정적으로 된 것을 확인해야 자동화에 문제가 없다.
- `all` : 모든 영역 / `rocky` : 정의한 영역

```
# 모든 호스트
ansible all -m shell -a "ifconfig" -k

# rocky 그룹 호스트
ansible rocky -m shell -a "ifconfig" -k
```

### (4) 유저 생성

- Master Node에서 모든 도메인 유저를 설정할 수 있다.

```
ansible all -m user -a "name=yslee" -k
```

### (6) Airflow 빌드 및 Project 설치 자동화
- Project clone 과정을 자동화한다. 아래의 두가지 옵션중에서 선택할 수 있다.
- (옵션 1) 아래 깃허브 레파지토리에서 프로젝트를 클론한다.
- (옵션 2) 더욱 간편한 작업을 위하여 Shell Script를 사용한다.
- 리눅스에서 `/root` 디렉토리에 `vi clone_police.sh`를 추가하고, 아래의 내용을 넣는다. 

```
# 수동 방식
git clone -b yslee --single-branch https://github.com/hugingstar/Police.git
```

```
# sh 파일 방식
cd ~
vi clone_police.sh

# 작성한 내용
# 1. 변수 설정
REPO_URL="https://github.com/hugingstar/Police.git"
BRANCH_NAME="yslee"
TARGET_DIR="Police"

echo "=== Git Clone 작업 시작: 브랜치 [$BRANCH_NAME] ==="

# 2. 동일한 이름의 디렉토리가 있는지 확인
if [ -d "$TARGET_DIR" ]; then
    echo "오류: '$TARGET_DIR' 디렉토리가 이미 존재합니다. 작업을 중단합니다."
    exit 1
fi

# 3. git clone 실행
# -b: 특정 브랜치 지정
# --single-branch: 해당 브랜치의 이력만 가져옴
git clone -b $BRANCH_NAME --single-branch $REPO_URL

# 4. 결과 확인
if [ $? -eq 0 ]; then
    echo "성공: [$BRANCH_NAME] 브랜치를 성공적으로 복사했습니다."
else
    echo "실패: Git 클론 도중 문제가 발생했습니다."
    exit 1
fi
```

```
# 실행 권한 부여
chmod +x clone_police.sh

# 실행
./clone_police.sh
```

#### Step2 (Install): 

- 이 과정에서는 Police라는 프로젝트를 clone이 완료된 상태이다. 
- 인프라 구축을 위한 기본적인 프로그램을 설치한다.

(1) Firewall > (2) Docker install > (3) Postgres installation on linux

```
ansible-playbook Police/ansinfra_process.yaml -k
```

#### Step3 (Containers): 

- 이 과정에서는 Airflow 빌드 및 모듈 셋팅과정을 자동화한다.

(4) Postgres server using docker > (5) Runnning Airflow > (6) Python files move to dags folder

```
ansible-playbook Police/ansinfra_airflow_build.yaml -k
```