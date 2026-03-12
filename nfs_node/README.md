# NFS

- 모든 서버가 공통으로 사용하는 중앙 창고
- DB 데이터 및 Log 데이터가 안전하게 쌓이는 곳
- **NFS 서버 IP** : '10.15.0.170'
- **공유 루트 디렉토리**: '/root/nfs_node'
```
## 2.서비스별 할당 경로
현재 인프라 노드에 아래와 같이 실제 디렉토리 생성이 완료되었습니다.
- '/root/nfs_node/static' (Web용) -> 'nfs-pvc-web'
- '/root/nfs_node/was' (Was용) -> 'nfs-pvc-was'
- '/root/nfs_node/db' (Database용) -> 'nfs-pvc-db'
- '/root/nfs_node/config' (설정 파일용) -> 'nfs-pvc-config'
- '/root/nfs_node/monitoring' (모니터링 데이터용) -> 'nfs-pvc-monitoring'
- '/root/nfs_node/airflow' (Airflow 작업용) -> 'nfs-pvc-airflow'
```
## 3. 쿠버네티스 적용 방법
팀원들은 마스터 노드에서 본 저장소를 'git pull' 받은 후, 아래 명령어를 순서대로 실행하여 스토리지를 연결하세요.

'''bash
# 1. PV 생성
kubectl apply -f nfs-pv/

# 2. PVC 생성
kubectl apply -f nfs-pvc/

# 3. 상태 확인 (STATUS가 Bound인지 확인)
kubectl get pv,pvc
### 클론 유의사항

- .gitignore는 꼭 Clone 시에 받아주세요.