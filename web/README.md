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

metallb.yaml 생성 
 pool 설정 
 ip 범위 잡아주기 

# https 설정
- 인증서 발급
```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout kojel.key -out kojel.crt \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=Kojel/CN=www.kojel.com"
kubectl create secret tls kojel-tls-secret \
  --cert=kojel.crt \
  --key=kojel.key \
  -n web
```
- web.yaml 수정
Configmap 에
 default.conf: |
    server {
        listen 80;
        listen 443 ssl;
        server_name kojel.com www.kojel.com;
        charset utf-8;
        ssl_certificate /etc/nginx/ssl/tls.crt;
        ssl_certificate_key /etc/nginx/ssl/tls.key;

        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
        location /api {
            proxy_pass http://localhost:8000/;
        }
    }

  Deployment 에
    containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        - containerPort: 443
        volumeMounts:
        - name: config-volume
          mountPath: /etc/nginx/conf.d/default.conf
          subPath: default.conf
        - name: config-volume
          mountPath: /usr/share/nginx/html/index.html
          subPath: index.html
        - name: ssl-certs
          mountPath: "/etc/nginx/ssl"
          readOnly: true

  service 에
  ports:
    - name: http
      protocol: TCP
      port: 80
      targetPort: 80
    - name: https
      protocol: TCP
      port: 443
      targetport: 443
       

# .yaml 수정 후 적용 
kubectl apply -f web.yaml

# 파드 재시작
kubectl rollout restart deployment fastweb-combined -n web
