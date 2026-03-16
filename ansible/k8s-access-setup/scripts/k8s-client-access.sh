#!/bin/bash 

echo "🚀 Start install kubectl"

# 1. Install dependencies
sudo apt update && apt install -y apt-transport-https ca-certificates curl

# 2. Add k8s's official GPG key
sudo mkdir -p -m 755 /etc/apt/keyrings 
sudo curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.29/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg

# 3. Add k8s's repository 
sudo echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.29/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo chmod 644 /etc/apt/sources.list.d/kubernetes.list

# 4. Install kubectl 
sudo apt get update
sudo apt install -y kubectl

echo "🎉 Finished install"