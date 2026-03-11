#web pod 

web.yaml *namespace-web으로 설정 
- ConfigMap
  name: nginx-config
  index.html 안에 임시로 작성 
  setvername, location 설정 

- Deployment
  name: fastweb-combined
  replicas: 2
  Lablels: 
    app: web-server

  containers:
    image: nginx:latest, python:3.9-slim

- Service
  name: login-service
  annotations:
    metallb.io/loadBalancerIPs: 10.22.0.10
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80

metallb.yaml