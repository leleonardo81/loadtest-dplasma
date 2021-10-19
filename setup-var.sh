#!/bin/bash

REGION=us-central1
ZONE=${REGION}-b
PROJECT=$(gcloud config get-value project)
CLUSTER=gke-load-test
TARGET=${PROJECT}.appspot.com
SCOPE="https://www.googleapis.com/auth/cloud-platform"

sed -i -e "s/\[PROJECT_ID\]/$PROJECT/g" kubernetes-config/locust-master-controller.yaml
sed -i -e "s/\[PROJECT_ID\]/$PROJECT/g" kubernetes-config/locust-worker-controller.yaml

