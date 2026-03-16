# 🚀 How Clients connect to a Kubernetes cluster
k8s-access-setup/ 에서 생성한 kubeconfig 파일을 작업자의 PC에 저장하고, 쿠버네티스 클러스터에 클라이언트로 접속하는 프로세스에 대해 기술하고 있습니다. 

## 🔍쿠버네티스 클러스터 접속 가이드 

1. 각자 전달 받은 conf-user-xxx.yaml 파일을 본인의 작업용 서버로 가져갑니다.
2. 파일 이름을 config로 바꾼 뒤, ~/.kube/ 폴더 안에 넣습니다.
    
    ```bash
    # 1. .kube 디렉토리 생성 
    > mkdir -p ~/.kube
    
    # 2. 복사한 파일 경로 이동 
    > mv conf-user-xxx.yml ~/.kube/config 
    
    # 3. 보안을 위해 권한 제한 (권장) 
    > chmod 600 ~/.kube/config 
    ```
    
3. k8s-client-access.sh를 clone 혹은 copy 후 스크립트를 실행합니다. 
    
    ```bash
    > ./k8s-client-access.sh
    ```
    
4. 쿠버네티스 클러스터 접속이 되는지 확인합니다. 
    
    ```bash
    # 설치 확인
    > kubectl version --client  
    # 노드 목록이 보이는지 확인 
    > kubectl get nodes
    ```
