#!/bin/bash

# 1. 변수 설정
REPO_URL="https://github.com/hugingstar/Police.git"
BRANCH_NAME="yslee"
TARGET_DIR="Police"
PLAYBOOK_PATH="/root/Police/ans_airflow_grafana_build.yaml"

echo "=== 작업 시작: Git Clone, Ansible 실행 및 Docker 상태 확인 ==="

# 2. 동일한 이름의 디렉토리가 있는지 확인
if [ -d "$TARGET_DIR" ]; then
    echo "오류: '$TARGET_DIR' 디렉토리가 이미 존재합니다. 작업을 중단합니다."
    exit 1
fi

# 3. git clone 실행
# -b: 특정 브랜치 지정 / --single-branch: 해당 브랜치의 이력만 가져옴
git clone -b $BRANCH_NAME --single-branch $REPO_URL

# 4. Clone 결과 확인
if [ $? -eq 0 ]; then
    echo "성공: [$BRANCH_NAME] 브랜치를 성공적으로 복사했습니다."
else
    echo "실패: Git 클론 도중 문제가 발생했습니다."
    exit 1
fi

# 5. Ansible Playbook 실행
# -k 옵션은 SSH password 입력을 요구하므로 프롬프트가 뜰 때 비밀번호를 입력해야 합니다.
echo "------------------------------------------------"
echo "Ansible Playbook 실행을 시작합니다."
echo "SSH 연결을 위한 비밀번호를 입력해주세요 (-k 옵션)."
echo "------------------------------------------------"

ansible-playbook $PLAYBOOK_PATH -k

# 6. Ansible 실행 결과 확인
if [ $? -eq 0 ]; then
    echo "성공: Ansible Playbook 실행이 완료되었습니다."
else
    echo "실패: Ansible Playbook 실행 중 오류가 발생했습니다."
    exit 1
fi

# 7. Docker 상태 확인 (추가된 부분)
echo "------------------------------------------------"
echo "최종 Docker 리소스 상태를 확인합니다."
echo "------------------------------------------------"

echo "[Docker 컨테이너 목록 (docker ps -a)]"
docker ps -a

echo ""
echo "[Docker 네트워크 목록 (docker network ls)]"
docker network ls

echo "------------------------------------------------"
echo "=== 모든 작업이 종료되었습니다. ==="