# Prometheus Node Exporter 자동화 배포 시스템 

## 개요 
- Ansible Playbook을 사용하여 다중 서버 Node Exporter 원격 설치를 자동화했습니다. 
- systemd 서비스 등록 및 실행 자동화를 통해 서버가 다운되거나 재시작해도 nodex exporter 연결을 유지할 수 있습니다. 
- SELinux 컨텍스트 자동 설정을 통해 실행 오류를 방지하였습니다. 
- 프로메테우스가 동적으로 읽어오는 NFS 서버의 동적 파일(.json)에 node-exporter 대상 서버를 추가합니다. 


## 기술 스택 
- Automation: Ansible, Bash Shell Script
- Monitoring: Prometheus, Node Exporter
- OS: Rocky Linux 

## 파일 구조 
```
.             
├── task/
|   ├── 01-install_exprter.yaml   # node-exporter 설치 및 systemd 서비스 등록 
|   └── 02-add-export-node.yml    # prometheus가 동적으로 읽어오는 json 파일에 서버 등록 
├── templates/
│   └── node-exporter.service.j2  # systemd 서비스 설정 템플릿
├── main.yaml                     # task 전체 실행 
└── README.md
```

## 실행 방법 
1. 인벤토리 IP 등록
아래와 같은 구조로 인벤토리 IP를 등록합니다. 
```
# /etc/ansible/hosts
# <<Target IP>> target_instance=<<InstanceName>> target_job=<<ExternalJob>>
[target_nodes]
x.x.x.x target_instance="mail-server" target_job="external-mail-server"
x.x.x.x target_instance="dns-server" target_job="external-dns-server"
```
2. 아래와 같이 main.yaml 파일을 실행합니다. 
```
ansible-playbook -i /etc/ansible/hosts main.yaml 
```
