# Infra installation automation for airflow

- Ansible 사용하여 Docker/Airflow 설치 과정을 자동화한다.
- 설치할 영역을 설정합니다.
- Cronjob 작업을 수행하고자 하는 IP를 작성합니다.

```
vi /etc/ansible/hosts

[yslee]
10.17.0.2
```

- yaml 파일은 github를 통해서 내려 받는다.

```
git clone -b yslee --single-branch https://github.com/hugingstar/Police.git
```

## Docker installation

- playbook 파일 구문을 체크한다.

```
cd ansible/docker
ansible-playbook docker_install.yaml --syntax-check
```

- playbook을 실행하여 Docker 설치 자동화 파일을 적용
- airflow 그룹에 해당하는 호스트에 일괄 적용

```
ansible-playbook docker_install.yaml -k
```

- 설치 완료 시 확인 방법

```
docker --version
```

- 작동 상태 확인 방법

```
systemctl status docker  
```

## Airflow installation

- playbook 파일 구문을 체크한다.

```
ansible-playbook airflow_install.yaml --syntax-check
```

- playbook을 실행하여 Docker 설치 자동화 파일을 적용
- airflow 그룹에 해당하는 호스트에 일괄 적용

```
ansible-playbook airflow_install.yaml -k
```

- 설치된 추가 패키지 확인하는 방법(Additional packages)
- 자신이 airflow_install.yaml 안에 추가한 사항을 확인하는 방법

```
docker compose exec airflow-worker pip list | grep -E "finance-datareader|pandas|numpy|psycopg2"
```


- airflow 컨테이너 별도로 삭제 방법

```
# 컨테이너 삭제
docker rm -f $(docker ps -aq --filter "name=cronjob")

# 이미지 삭제
docker rmi $(docker images 'cronjob-airflow*' -q)
```


## Postgres installation

- playbook 파일 구문을 체크한다.

```
ansible-playbook postgres_install.yaml --syntax-check
```

- playbook을 실행하여 Docker 설치 자동화 파일을 적용
- airflow 그룹에 해당하는 호스트에 일괄 적용

```
ansible-playbook postgres_install.yaml -k
```

- 버전 확인

```
psql --version
```

## Disable Firewall

- playbook 파일 구문을 체크한다.

```
ansible-playbook firewall.yaml --syntax-check
```

- playbook을 실행하여 Docker 설치 자동화 파일을 적용
- airflow 그룹에 해당하는 호스트에 일괄 적용

```
ansible-playbook firewall.yaml -k
```

- 버전 확인

```
systemctl status firewalld
```