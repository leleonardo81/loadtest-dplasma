#!/bin/bash

gcloud builds submit --tag gcr.io/$PROJECT/locust-tasks:latest docker-image
gcloud container images list | grep locust-tasks