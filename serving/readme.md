# Serving Folder

This folder contains the FastAPI-based model serving API for real-time inference.

- **Loads models from MLflow** (artifacts stored in MinIO) at startup, supporting both production and shadow models.
- **Exposes a `/predict` endpoint** that receives input features and returns predictions. Each request is processed by both production and shadow models for comparison.
- **Streams prediction events to Kafka** for downstream monitoring and analysis (e.g., in Elasticsearch).
- **Exports Prometheus metrics** (latency, CPU, memory, etc.) for monitoring via Prometheus and Grafana.
- **Modular code structure**: Core logic is organized in the `services/` folder (model inference, Kafka, metrics).
- **Configurable via environment variables** for model name, Kafka broker, MLflow URI, and more.

This service is the main entry point for real-time model inference in the platform, enabling observability, event streaming, and robust monitoring for production ML workflows.
