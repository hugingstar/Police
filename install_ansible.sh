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