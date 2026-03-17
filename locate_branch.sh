#!/bin/bash

# 1. 대상 디렉토리 및 브랜치 정의 (경로:브랜치)
REPOS=(
    "/root/nfs_node/static/jjh:jjh"
    "/root/nfs_node/monitoring/kjs:kjs"
    "/root/nfs_node/was/yslee:yslee"
    "/root/nfs_node/db/ohit:ohit"
)

GIT_URL="https://github.com/hugingstar/Police.git"

echo "Git Clone 작업을 시작합니다. (기존 데이터가 있으면 삭제 후 덮어씁니다)"

for item in "${REPOS[@]}"; do
    # 경로와 브랜치 분리
    DIR="${item%%:*}"
    BRANCH="${item##*:}"

    echo "----------------------------------------------------"
    echo "목표 경로: $DIR"
    echo "브랜치: $BRANCH"

    # 2. 기존 디렉토리가 존재하면 삭제 (덮어쓰기 핵심)
    if [ -d "$DIR" ]; then
        echo "기존 디렉토리를 삭제하고 새로 클론합니다: $DIR"
        rm -rf "$DIR"
    fi

    # 3. 디렉토리 생성 및 이동
    mkdir -p "$DIR"
    cd "$DIR" || { echo "경로 이동 실패: $DIR"; continue; }

    # 4. 클론 진행
    echo "클론 중: $BRANCH 브랜치..."
    git clone -b "$BRANCH" --single-branch "$GIT_URL" .
done

echo "----------------------------------------------------"
echo "모든 덮어쓰기 작업이 완료되었습니다."