# Daily Market Monitoring

- Airflow가 실행되어 있는 상태에서 실행하여야 한다.
- Data Collector와 Data Analysis 모듈들은 ansible 스크립트를 사용하여 airflow 내에 있는 dags로 위치시킨다.

```
# 데이터 수집 모듈을 dags에 위치
ansible-playbook analysis_to_dags.yaml -k

# 분석 결과 출력 모듈을 dags에 위치
ansible-playbook analysis_to_dags.yaml -k
```

- 이 모듈은 상위 디렉토리에 있는 `ansinfra_airflow_build.yaml`에 하위 작업으로 포함된다.