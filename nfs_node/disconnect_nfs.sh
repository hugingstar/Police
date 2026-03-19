#!/bin/bash

echo ">>> NFS 마운트 해제 및 디렉토리 정리를 시작합니다..."

umount -l /root/nfs_node/Data/KOSPI/A1Sheet
umount -l /root/nfs_node/Data/KOSPI/B1Sheet

umount -l /root/nfs_node/Data/KOSDAQ/A1Sheet
umount -l /root/nfs_node/Data/KOSDAQ/B1Sheet

umount -l /root/nfs_node/Data/NASDAQ/A1Sheet
umount -l /root/nfs_node/Data/NASDAQ/B1Sheet

umount -l /root/nfs_node/Data/NYSE/A1Sheet
umount -l /root/nfs_node/Data/NYSE/B1Sheet

echo ">>> 모든 NFS 마운트가 해제되었습니다."

echo ">>> 작업이 완료되었습니다."