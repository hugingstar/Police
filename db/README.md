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
# 마운트를 위해서 권한을 준다.
chmod 777 /root/nfs_node/db/ohit/db/sql

# 서비스 시작
kubectl apply -f mariadb-service.yaml -n db

# 서비스 상태 확인
kubectl get po,svc,deploy -n db

# 정상적으로 실행되고 있는지 확인
kubectl get pods -l app=mariadb

# DB가 정상적으로 실행되었는지 확인
kubectl logs -f deployment/mariadb-deployment

# 서비스 삭제
kubectl delete -f mariadb-service.yaml -n db
```













### 3. 데이터 임포트 및 복구 절차
로컬(10.15.0.150)에 보관된 SQL 덤프 파일을 Pod 내부로 주입하여 데이터를 구성하였습니다.
kubectl exec -i mariadb-pod -- mariadb -u root -p'P@ssw0rd' userdb < userdb.sql