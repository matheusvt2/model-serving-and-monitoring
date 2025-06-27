# Versioning Folder

This folder contains configuration and persistent data for model versioning and artifact storage:

- **MLflow**: Tracks experiments, manages the model registry, and logs model metadata.
- **MinIO**: Stores model artifacts and files in S3-compatible object storage.
- **Database (Postgres)**: Stores MLflow experiment metadata and tracking data.

All configuration files and persistent data are stored here and mounted as volumes in the respective containers. This folder is essential for experiment tracking, model registry, and artifact management in the ML pipeline.
