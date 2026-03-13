# Prometheus Node Exporter 자동화 배포 시스템 

## 개요 
- Ansible Playbook을 사용하여 다중 서버 Node Exporter 원격 설치를 자동화했습니다. 
- systemd 서비스 등록 및 실행 자동화를 통해 서버가 다운되거나 재시작해도 nodex exporter 연결을 유지할 수 있습니다. 
- SELinux 컨텍스트 자동 설정을 통해 실행 오류를 방지하였습니다. 
- 쉘 스크립트를 이용해 인벤토리 IP 중복 체크 및 자동 추가 기능으로 효율적인 관리가 가능합니다. 

## 기술 스택 
- Automation: Ansible, Bash Shell Script
- Monitoring: Prometheus, Node Exporter
- OS: Rocky Linux 

## 파일 구조 
```
.             
├── install_exporter.sh  # IP 중복 체크 및 playbook 실행용 쉘 스크립트
├── node_exporter.yml    # 메인 Ansible Playbook
├── templates/
│   └── node-exporter.service.j2  # systemd 서비스 설정 템플릿
└── README.md
```

## 실행 방법 
```
chmod +x install_exporter.sh
./new-node-exporter.sh x.x.x.x #추가할 서버 IP
```
