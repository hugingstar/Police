#!/bin/bash

kubectl delete svc,deploy mariadb-service -n db

kubectl get all -n db