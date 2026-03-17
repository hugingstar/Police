#!/bin/bash

# 1. 대상 디렉토리 및 브랜치 정의 (경로:브랜치)
REPOS=(
    "/root/nfs_node/static/jjh:jjh"
    "/root/nfs_node/monitoring/kjs:kjs"
    "/root/nfs_node/was/yslee:yslee"
    "/root/nfs_node/db/ohit:ohit"
)

GIT_URL="https://github.com/hugingstar/Police.git"

echo "작업 시작 시간: $(date)"

for item in "${REPOS[@]}"; do
    DIR="${item%%:*}"
    BRANCH="${item##*:}"

    echo "----------------------------------------------------"
    echo "체크 경로: $DIR ($BRANCH 브랜치)"

    # 디렉토리가 없으면 일단 생성 후 클론
    if [ ! -d "$DIR/.git" ]; then
        echo "저장소가 존재하지 않습니다. 새로 클론합니다."
        mkdir -p "$DIR"
        cd "$DIR" || continue
        git clone -b "$BRANCH" --single-branch "$GIT_URL" .
        continue
    fi

    # 디렉토리가 있으면 변경사항 확인
    cd "$DIR" || continue
    
    # 원격 정보 업데이트
    git fetch origin "$BRANCH" > /dev/null 2>&1

    LOCAL_HASH=$(git rev-parse HEAD)
    REMOTE_HASH=$(git rev-parse "origin/$BRANCH")

    if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
        echo "변경사항이 감지되었습니다! ($LOCAL_HASH -> $REMOTE_HASH)"
        echo "기존 데이터를 삭제하고 새로 클론합니다."
        
        # 안전하게 상위로 이동 후 삭제 및 재생성
        cd ..
        rm -rf "$DIR"
        mkdir -p "$DIR"
        cd "$DIR" || continue
        git clone -b "$BRANCH" --single-branch "$GIT_URL" .
    else
        echo "변경사항이 없습니다. 작업을 건너뜁니다."
    fi
done

echo "----------------------------------------------------"
echo "작업 종료 시간: $(date)"