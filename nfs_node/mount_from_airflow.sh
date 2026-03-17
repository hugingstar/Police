echo ">>> NFS 마운트를 시작합니다..."

# 1. 마운트될 폴더들 생성 (이미 있으면 통과)
mkdir -p /root/nfs_node/Data/KOSPI/A1Sheet /root/nfs_node/Data/KOSPI/B1Sheet
mkdir -p /root/nfs_node/Data/KOSDAQ/A1Sheet /root/nfs_node/Data/KOSDAQ/B1Sheet
mkdir -p /root/nfs_node/Data/NASDAQ/A1Sheet /root/nfs_node/Data/NASDAQ/B1Sheet
mkdir -p /root/nfs_node/Data/NYSE/A1Sheet /root/nfs_node/Data/NYSE/B1Sheet

# 2. KOSPI 마운트
mount -t nfs 10.17.0.2:/root/Data/KOSPI/A1Sheet /root/nfs_node/Data/KOSPI/A1Sheet
mount -t nfs 10.17.0.2:/root/Data/KOSPI/B1Sheet /root/nfs_node/Data/KOSPI/B1Sheet

# 3. KOSDAQ 마운트
mount -t nfs 10.17.0.2:/root/Data/KOSDAQ/A1Sheet /root/nfs_node/Data/KOSDAQ/A1Sheet
mount -t nfs 10.17.0.2:/root/Data/KOSDAQ/B1Sheet /root/nfs_node/Data/KOSDAQ/B1Sheet

# 4. NASDAQ 마운트
mount -t nfs 10.17.0.2:/root/Data/NASDAQ/A1Sheet /root/nfs_node/Data/NASDAQ/A1Sheet
mount -t nfs 10.17.0.2:/root/Data/NASDAQ/B1Sheet /root/nfs_node/Data/NASDAQ/B1Sheet

# 5. NYSE 마운트
mount -t nfs 10.17.0.2:/root/Data/NYSE/A1Sheet /root/nfs_node/Data/NYSE/A1Sheet
mount -t nfs 10.17.0.2:/root/Data/NYSE/B1Sheet /root/nfs_node/Data/NYSE/B1Sheet

echo ">>> 마운트 완료!"
echo "------------------------------------------------------"

# 6. 디스크 상태 확인
df -h
