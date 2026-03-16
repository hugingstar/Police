#!/bin/bash

# --- 설정 구간 ---
# 저장소를 클론할 절대 경로를 입력하세요. (예: /home/유저명/Police)
TARGET_DIR="$HOME/Police"
REPO_URL="https://github.com/hugingstar/PoliceInfra.git"
BRANCH="master"
# ----------------

# 1. 대상 디렉토리가 없으면 최초 클론 수행
if [ ! -d "$TARGET_DIR" ]; then
    echo "저장소가 존재하지 않아 클론을 시작합니다..."
    git clone -b $BRANCH $REPO_URL $TARGET_DIR
    exit 0
fi

# 2. 디렉토리 이동
cd "$TARGET_DIR" || exit

# 3. 원격 저장소 정보 업데이트 (실제 다운로드는 아님)
git fetch origin $BRANCH

# 4. 로컬과 원격의 최신 커밋 해시 비교
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/$BRANCH)

if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
    echo "$(date): 새로운 변화가 감지되었습니다. 업데이트를 진행합니다."
    git pull origin $BRANCH
else
    echo "$(date): 변경 사항이 없습니다."
fi