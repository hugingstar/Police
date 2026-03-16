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

# Alone command
- 관리자가 추가적으로 분석이 필요한 날의 결과를 출력하는 곳이다.
- 조건 : A1Sheet가 완료된 상태이어야 한다.

```
# 날짜 지정하여 실행
python main.py --start 2026-01-01 --end 2026-03-15

# 인자에 대한 도움말
python main.py --help
```
