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