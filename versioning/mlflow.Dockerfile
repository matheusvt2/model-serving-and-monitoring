# No custom Dockerfile needed for MinIO. Using official image in docker-compose. 
FROM ghcr.io/mlflow/mlflow:v3.1.1

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir boto3==1.37.11 psycopg2-binary==2.9.10