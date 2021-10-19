#!/bin/bash

kubectl rollout restart deployment locust-master
kubectl rollout restart deployment locust-worker
