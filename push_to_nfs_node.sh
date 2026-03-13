#!/bin/bash

# 1. nfs-utils 설치
echo "NFS 유틸리티를 설치합니다..."
dnf install -y nfs-utils

# 2. 공유 설정 정의 (경로와 옵션을 1:1로 매칭)
# 형식: "경로|옵션"
# 나중에 특정 경로의 IP나 권한만 바꾸고 싶다면 이 리스트에서 해당 줄만 수정하세요.
CONFIGS=(
    "/root/Data/KOSPI/A1Sheet|10.15.0.150(rw,sync,no_root_squash)"
    "/root/Data/KOSPI/B1Sheet|10.15.0.150(rw,sync,no_root_squash)"
    "/root/Data/KOSDAQ/A1Sheet|10.15.0.150(rw,sync,no_root_squash)"
    "/root/Data/KOSDAQ/B1Sheet|10.15.0.150(rw,sync,no_root_squash)"
    "/root/Data/NASDAQ/A1Sheet|10.15.0.150(rw,sync,no_root_squash)"
    "/root/Data/NASDAQ/B1Sheet|10.15.0.150(rw,sync,no_root_squash)"
    "/root/Data/NYSE/A1Sheet|10.15.0.150(rw,sync,no_root_squash)"
    "/root/Data/NYSE/B1Sheet|10.15.0.150(rw,sync,no_root_squash)"
)

echo "디렉토리 생성 및 /etc/exports 설정을 시작합니다..."

for entry in "${CONFIGS[@]}"; do
    # 파이프(|) 기호를 기준으로 경로와 옵션을 분리합니다.
    SHARE_DIR="${entry%%|*}"
    NFS_OPTION="${entry##*|}"

    # 디렉토리 생성 (없을 경우)
    if [ ! -d "$SHARE_DIR" ]; then
        echo "디렉토리 생성 중: $SHARE_DIR"
        mkdir -p "$SHARE_DIR"
    fi

    # /etc/exports 설정 추가 (정확한 매칭을 위해 경로와 옵션을 합쳐서 체크)
    EXPORT_LINE="$SHARE_DIR $NFS_OPTION"
    
    # 이미 해당 경로에 대한 설정이 있는지 확인 (경로명으로 검색)
    if ! grep -qF "$SHARE_DIR" /etc/exports; then
        echo "설정 추가: $EXPORT_LINE"
        echo "$EXPORT_LINE" | sudo tee -a /etc/exports > /dev/null
    else
        echo "이미 설정이 존재하여 건너뜁니다: $SHARE_DIR"
        # 팁: 기존 설정을 덮어쓰고 싶다면 여기서 sed 등을 사용해 교체할 수 있습니다.
    fi
done

# 3. 설정 적용
echo "NFS 수출 테이블을 갱신합니다..."
exportfs -rav

# 4. 서비스 시작 및 활성화
echo "NFS 서버 서비스를 시작하고 활성화합니다..."
systemctl enable --now nfs-server

echo "모든 NFS 경로 설정이 완료되었습니다."