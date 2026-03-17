# MariaDB service
- 데이터베이스 설치

## Persistent volume and Persistent volume claim
- PV ohit 브랜치의 파일을 Github에서 내려받는다.

```
git clone -b ohit --single-branch https://github.com/hugingstar/Police.git
```

- 해당 작업 경로로 들어가서 권한 부여 후 작동한다.

```
# 작업 경로로 이동
cd /root/Police/db

# Volume 실행
chmod +x volume_auto_run.sh
./volume_auto_run.sh

# Volume claim 실행
chmod +x volume_auto_down.sh
./volume_auto_down.sh

```

## k8s Deployment, Service

- MariaDB Pod를 Service로 시작한다.
- 데이터베이스 특성상 ReadWriteOnce NFS를 사용할 경우 1을 권장한다.

```
kubectl apply -f mariadb-service.yaml

# 정상적으로 실행되고 있는지 확인
kubectl get pods -l app=mariadb

# DB가 정상적으로 실행되었는지 확인
kubectl logs -f deployment/mariadb-deployment
```














쿠버네티스 적용 방법
팀원들은 마스터 노드에서 본 저장소를 'git pull' 받은 후, 아래 명령어를 순서대로 실행하여 스토리지를 연결하세요.

'''bash
# 1. PV 생성
kubectl apply -f nfs-pv/

# 2. PVC 생성
kubectl apply -f nfs-pvc/



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


## MariaDB 데이터베이스 구축 및 설정

본 프로젝트의 데이터 관리를 위해 수행한 MariaDB 인프라 구축 과정입니다.

### 1. MariaDB 컨테이너 환경 구축
- **배포 환경:** Kubernetes (Ubuntu 10.15.0.150 노드 기반)
- **컨테이너 이미지:** 'mariadb:10.6'
- **주요 설정:**
 - 'MYSQL_ROOT_PASSWORD': 'P@ssw0rd'
 - 'Port' : 3306

 ### 2. 데이터베이스 및 스키마 생성
 최초 배포 후 애플리케이션에서 사용할 데이터베이스와 테이블 구조를 수동으로 정의하였습니다.
 - **Database 생성:** `CREATE DATABASE userdb;`
 - **구조 확인:** `DESC userdb.members;` 명령어를 통해 필드 및 데이터 타입 검증 완료

### 3. 데이터 임포트 및 복구 절차
로컬(10.15.0.150)에 보관된 SQL 덤프 파일을 Pod 내부로 주입하여 데이터를 구성하였습니다.
kubectl exec -i mariadb-pod -- mariadb -u root -p'P@ssw0rd' userdb < userdb.sql