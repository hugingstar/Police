# WAS 배포 및 회수 자동화

- 프로젝트 파일 내려받기

```
git clone -b yslee --single-branch https://github.com/hugingstar/Police.git
```


- WAS 서비스 배포 자동화 Shell

```
# 권한 부여
chmod +x k8s_was_service.sh

# 배포 시작
./k8s_was_service.sh
```

- k8s 배포 상태 확인 방법

```
kubectl get po,svc,deploy -n was
```

- WAS 서비스 회수 자동화 Shell

```
# 권한 부여 및 배포
chmod +x k8s_was_down.sh

# 회수 시작
./k8s_was_down.sh
```

