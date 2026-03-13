#!/bin/bash

NEW_IP=$1
TARGET_FILE="/etc/ansible/hosts"

if grep -qx "$NEW_IP" "$TARGET_FILE"; then 
    echo "Already add IP: $NEW_IP"
else 
    sed -i "/\[target_nodes\]/a $NEW_IP" "$TARGET_FILE"
    echo "Finished add IP: $NEW_IP"
fi 

echo "Start Node Exporter to $NEW_IP"
ansible-playbook install-exporter.yaml --limit "$NEW_IP"
echo "End ..."