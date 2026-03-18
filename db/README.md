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

# 서비스 삭제
kubectl delete -f mariadb-service.yaml -n db
```