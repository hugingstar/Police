# 🚀 Kubernetes Team Access Provisioning

이 프로젝트는 팀원별로 독립된 작업 환경(Namespace)을 제공하고, 최소 권한 원칙(PoLP)에 기반한 클러스터 접속 환경을 구축하는 프로세스를 담고 있습니다.

## 📋 개요
- **환경:** Ubuntu 22.04 (OS) / Kubernetes v1.29.15 (Server)
- **목적:** 팀원별 전용 계정 발급 및 서비스 레이어별 네트워크 격리 준비
- **주요 설정:** RBAC(Role-Based Access Control) 기반 권한 관리

<br>

## 📂 디렉토리 구조 및 역할
```
.
├── task/
|   ├── 01_namespaces.yaml         # web, was, db 등 생성
|   ├── 02_cluster_role.yaml       # 개발자 공통 권한 정의
|   ├── 03_setup_users.yaml        # SA 및 RoleBinding 설정
|   ├── 04_generate_secrets.yaml   # Token 발행용 Secret 설정
|   └── 05_extract_configs.sh      # kubeconfig 자동 생성 스크립트
├── scripts/                        
|   └── k8s-client-access.sh       # k8s 마스터 노드 접속 스크립트
└──
```

**1. 네임스페이스 생성 (`01-namespaces.yaml`)**
프로젝트 아키텍처(Web-WAS-DB-Collector)에 맞춘 논리적 격리 공간을 생성합니다.
- 생성 대상: `web`, `was`, `db`, `monitoring`, `data-pipeline`

**2. 공통 Role 정의 (`02-cluster-role.yaml`)**
팀원들이 공통으로 가질 권한을 정의합니다. 보안을 위해 `nodes`, `namespaces` 등 인프라 핵심 자원에 대한 수정 권한은 제외되었습니다.

**3. 서비스 어카운트 및 바인딩 (`03-setup-users.yaml`)**
각 팀원(lys, oit, jjh, kjs)을 위한 `ServiceAccount`를 생성하고, Step 2에서 만든 Role을 연결합니다.

**4️. 인증 토큰 발행 (`04-generate-secrets.yaml`)**
K8s 1.24+ 버전에 맞춰 SA용 `Secret`을 수동으로 생성하여 접속에 필요한 Long-lived Token을 확보합니다.

**5️. kubeconfig 생성 및 배포 (`05-extract-configs.sh`)**
마스터 노드에서 CA 데이터와 Token을 추출하여 팀원별 접속 파일(`conf-user-xxx.yaml`)을 생성합니다.

<br>

## 🔍쿠버네티스 클러스터 접속 가이드 
### 권한 정책 안내 

본 클러스터는 **최소 권한 원칙(PoLP)** 에 따라 계정별 Role을 적용하였습니다. 

다만, 현재 프로젝트 초기 단계로 세부 역할 분배가 유동적이고 팀원 간 원활한 협업을 지원하기 위해 서비스 운영에 필요한 자원에 대해서는 충분한 권한을 부여하고 인프라 핵심 자원에 대해서만 최소한의 제한을 두었습니다. 

</aside>

### 네임스페이스 이용 
작업 환경은 용도별로 다음과 같이 분리되어 있습니다. 
- `web`, `was`, `db`, `monitoring`, `collector`

네임스페이스 자체의 생성 및 삭제는 불가하오니, 반드시 지정된 네임스페이스 내에서 작업을 진행해 주시기 바랍니다.

### 쿠버네티스 접속 방법 
**scripts/k8s-client-access.sh 스크립트** 를 실행합니다. 
자세한 설명은 해당 `README.md`를 확인해주세요! 