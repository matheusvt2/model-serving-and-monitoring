# ONBOARDING GUIDE

Welcome to the Model Serving and Monitoring Platform! This guide will help you understand each component, how they connect, and why monitoring and event collection are essential for modern machine learning systems.

---

## 🚦 Pre-requisites

Before you start, make sure your system meets the following minimum requirements:

- **Operating System:** Linux/Unix
- **Memory:** 16 GB RAM (minimum)
- **CPU:** 4 CPU cores (minimum)
- **Disk:** 10 GB free space recommended
- **Docker:** [Install Docker](https://docs.docker.com/get-docker/)
- **Docker Compose:** [Install Docker Compose](https://docs.docker.com/compose/install/)

> **Why these requirements?**
> Running multiple containers for databases, message brokers, and ML services is resource-intensive. Insufficient resources may cause services to fail or run slowly.

---

## 🧩 Service Overview & Connections

Below, each service is explained in detail, including its role, how it connects to others, and why it matters in the pipeline.

### 1. **MLflow**

- **Role:** Model tracking, versioning, and registry.
- **How it connects:**
  - Stores model artifacts in **MinIO** (S3-compatible storage).
  - Uses **Postgres** (or SQLite) as a backend database for experiment metadata.
  - The **Serving API** loads models from MLflow.
- **Why:** Enables reproducibility, model management, and easy deployment of new versions.

### 2. **MinIO**

- **Role:** S3-compatible object storage for model artifacts.
- **How it connects:**
  - Receives model files from **MLflow**.
  - The **Serving API** fetches model binaries from MinIO via MLflow.
- **Why:** Decouples storage from compute, supports large files, and is cloud-native.

### 3. **Postgres**

- **Role:** Database for MLflow experiment metadata (runs, parameters, metrics).
- **How it connects:**
  - Used by **MLflow** as its backend store.
- **Why:** Ensures reliable, queryable storage of experiment history.

### 4. **Kafka**

- **Role:** Event streaming platform for prediction events.
- **How it connects:**
  - The **Serving API** sends every prediction (input, output, metadata) as an event to Kafka.
  - **Kafka Connect** and a custom **streaming service** consume these events.
- **Why:** Decouples event production and consumption, enables real-time analytics and monitoring.

### 5. **Kafka Connect**

- **Role:** Integration tool for moving data between Kafka and other systems.
- **How it connects:**
  - Reads prediction events from **Kafka**.
  - Writes them to **Elasticsearch** for indexing and search.
- **Why:** Automates data movement, supports scalable pipelines.

### 6. **Elasticsearch**

- **Role:** Search and analytics engine for prediction events.
- **How it connects:**
  - Receives events from **Kafka Connect** or the streaming service.
  - **Grafana** queries Elasticsearch to visualize prediction data.
- **Why:** Enables fast search, filtering, and aggregation of prediction logs.

### 7. **Prometheus**

- **Role:** Metrics collection and monitoring system.
- **How it connects:**
  - Scrapes metrics from the **Serving API** (e.g., prediction latency, CPU, memory).
  - **Grafana** uses Prometheus as a data source for real-time metrics.
- **Why:** Provides observability into system and model performance.

### 8. **Grafana**

- **Role:** Visualization and dashboarding tool.
- **How it connects:**
  - Connects to **Prometheus** for metrics and **Elasticsearch** for event data.
  - Displays dashboards for model performance, resource usage, and event analysis.
- **Why:** Makes monitoring actionable and accessible for all stakeholders.

### 9. **FastAPI Serving API**

- **Role:** Serves ML model predictions via a REST API.
- **How it connects:**
  - Loads models from **MLflow** (artifacts in **MinIO**).
  - Sends prediction events to **Kafka**.
  - Exposes Prometheus metrics for monitoring.
- **Why:** Provides a production-ready, observable interface for real-time inference.

---

## 🔗 How Services Connect: The Data Flow

1. **Model Training:**
   - You train a model in a notebook and log it to MLflow.
   - MLflow stores the model in MinIO and records metadata in Postgres.
2. **Model Serving:**
   - The FastAPI Serving API loads the latest model from MLflow/MinIO.
   - When a prediction is requested, it returns the result and sends an event to Kafka.
3. **Event Streaming:**
   - Kafka buffers prediction events.
   - Kafka Connect (or a custom streaming service) reads from Kafka and writes to Elasticsearch.
4. **Monitoring:**
   - Prometheus scrapes metrics from the Serving API (latency, CPU, memory).
   - Grafana visualizes both metrics (from Prometheus) and events (from Elasticsearch).

---

## 📈 Why Collect Metrics and Predictions?

- **Metrics (latency, CPU, memory, error rates):**
  - Help you detect performance bottlenecks, resource leaks, and outages.
  - Allow you to set up alerts for abnormal behavior (e.g., slow predictions, high memory usage).
  - Enable capacity planning and cost optimization.

- **Prediction Events (inputs, outputs, metadata):**
  - Provide a detailed audit trail for every prediction made.
  - Allow you to analyze model drift, data quality, and user behavior over time.
  - Enable comparison between production and shadow models (A/B testing, canary releases).
  - Support root-cause analysis when things go wrong (e.g., why did the model make a bad prediction?).

- **Together:**
  - Metrics and events give you a complete picture of both system health and model quality.
  - They are the foundation for continuous improvement, compliance, and trustworthy AI.

---

## 🏁 Next Steps

- Make sure you have Docker and Docker Compose installed.
- Follow the README for setup and usage instructions.
- Explore the dashboards in Grafana to see your pipeline in action!

If you have questions, reach out to the project maintainer or check the documentation links in the README.
