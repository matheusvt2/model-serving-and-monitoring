# Model Serving and Monitoring Platform

A full-stack, containerized machine learning platform for model training, versioning, serving, monitoring, and automated event streaming.  
This project demonstrates best practices for MLOps using Docker Compose, MLflow, MinIO, Prometheus, Grafana, Kafka, Elasticsearch, and Flask.

---

## ✨ Project Overview

- **Model Training & Versioning:** Train and log models with MLflow, storing artifacts in MinIO (S3-compatible).
- **Model Serving:** Serve predictions via a Flask API, with Prometheus metrics and Kafka event streaming.
- **Streaming & Monitoring:** Stream all prediction events to Kafka, persist in Elasticsearch, and visualize in Grafana.
- **Metrics & Retraining:** Monitor service and model metrics with Prometheus/Grafana; foundation for auto-retraining pipelines.

---

## 📋 Rules & Best Practices

- All services run in Docker containers and communicate on a shared network.
- All configuration and persistent data are stored in versioned folders and mounted as volumes.
- All sensitive/configurable values are managed via a `.env` file.
- Logging uses appropriate levels and is in English.
- All code and documentation are in English.

---

## 🏗️ High-Level Architecture

```mermaid
graph TD
    subgraph Versioning
        MLflow
        MinIO
        Postgres
    end
    subgraph Modeling
        Notebook
    end
    subgraph Serving
        FlaskAPI
    end
    subgraph Streaming
        Kafka
        KafkaConnect
        StreamPy
    end
    subgraph Monitoring
        Prometheus
        Grafana
        Elasticsearch
    end

    Notebook-->|logs model|MLflow
    MLflow-->|stores artifacts|MinIO
    FlaskAPI-->|loads model|MLflow
    FlaskAPI-->|sends metrics|Prometheus
    FlaskAPI-->|sends events|Kafka
    Kafka-->|streams events|StreamPy
    StreamPy-->|indexes|Elasticsearch
    Prometheus-->|metrics|Grafana
    Elasticsearch-->|events|Grafana
```

---

## ✅ Component Checklist

- [x] **Model**: Training notebook and pipeline (`modeling/`)
- [x] **Containerization**: Dockerfiles for all services
- [x] **Serving**: Flask API with Prometheus and Kafka integration (`serving/`)
- [x] **Monitoring**: Prometheus, Grafana, Elasticsearch, Kafka Connect (`monitoring/`, `communication/`)
- [x] **Auto retraining**: Foundation in place (extendable)
- [x] **Pipeline**: End-to-end event and metric flow

---

## 📂 Folder Structure

- `modeling/` — Model training, pipeline, and requirements
- `versioning/` — MLflow, MinIO, and database storage/config
- `serving/` — Flask API, Dockerfile, and model loading
- `communication/` — Kafka, Kafka Connect, streaming scripts
- `monitoring/` — Prometheus, Grafana, Elasticsearch configs/data
- `scripts/` — Utility scripts for testing and monitoring (see below)
- `docker-compose.yaml` — All services and network configuration

---

## 🚀 Quickstart

### 1. Clone and Configure

```bash
git clone <your-repo-url>
cd model-serving-and-monitoring
cp .env.example .env  # Edit as needed
```

### 2. Build and Start All Services

```bash
docker-compose up --build
```

### 3. Create MinIO Bucket for MLflow

- Access MinIO Console: [http://localhost:9001](http://localhost:9001)
- Login with credentials from `.env`
- **Create a bucket named `mlflow`**

### 4. Train and Register a Model

- Open and run `modeling/classif.ipynb` (Jupyter or VSCode)
- Model and artifacts will be logged to MLflow and MinIO

### 5. Serve Predictions

- Start the serving API (already in Docker Compose)
- Send test requests:
  ```bash
  bash scripts/calls.sh "[5.1,3.5,1.4,0.2]" --repetitions=5
  bash scripts/calls.sh --repetitions=10
  ```

---

## 📊 Monitoring & Visualization

### Grafana

- Access: [http://localhost:3000](http://localhost:3000)
- **Default login:** `admin` / `admin` (or as set in `.env`)

#### Add Elasticsearch Data Source

1. Go to **Gear (⚙️) > Data Sources**
2. Click **Add data source** → **Elasticsearch**
3. **URL:** `http://elasticsearch:9200`
4. **Index name:** `predictions`
5. **Elasticsearch version:** `8.x`
6. **Time field name:** `@timestamp`
7. **Save & Test**

#### Add Prometheus Data Source

1. Go to **Gear (⚙️) > Data Sources**
2. Click **Add data source** → **Prometheus**
3. **URL:** `http://prometheus:9090`
4. **Save & Test**

#### Example Panel: Predictions per Category

- Create a new panel
- **Query:**  
  - Metric: `Count`
  - Group by: `prediction_text.Species.keyword` or `prediction_label`
- Set time range as needed

---

### 🚦 Model Comparison Dashboard (Grafana)

A ready-to-import dashboard is provided at `monitoring/grafana/model_comparison_dashboard.json`.

#### **How to Import**
1. In Grafana, go to **Dashboards > New > Import**.
2. Upload or paste the JSON from `monitoring/grafana/model_comparison_dashboard.json`.
3. Select your Prometheus and Elasticsearch data sources when prompted.

#### **What This Dashboard Shows**
- **Prediction counts** for both models (from Elasticsearch)
- **Prediction duration, CPU, and memory** for both models (from Prometheus)
- **Class distribution** for both models (from Elasticsearch)
- **Agreement table**: Compare predictions for the same request using `event_uuid`
- **Side-by-side performance and statistics** for production and shadow models

#### **How to Extend**
- Add panels for accuracy, confusion matrix, or custom agreement logic using `event_uuid` and prediction fields.
- Use Prometheus queries to create alerts or advanced performance comparisons.
- Use Elasticsearch queries to analyze model drift, class imbalance, or disagreement rates.

---

## 🛠️ Troubleshooting

- **Grafana Permission Error:**  
  ```bash
  sudo chmod -R 777 ./monitoring/grafana
  ```
- **Check Event Count in Elasticsearch:**  
  ```bash
  bash scripts/check_events.sh
  ```

- **Check if Events Were Sent to Elasticsearch:**
  
  The script `scripts/check_events.sh` checks whether there are any prediction events indexed in Elasticsearch. It queries the `predictions` index and prints the number of events found. This is useful for verifying that your pipeline is sending data to Elasticsearch correctly.
  
  Usage:
  ```bash
  bash scripts/check_events.sh
  ```

---

## 🔗 Useful Links

- [MLflow + MinIO Setup Guide](https://blog.min.io/setting-up-a-development-machine-with-mlflow-and-minio/)
- [Elasticsearch Docker Docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
- [Prometheus Docs](https://prometheus.io/docs/introduction/overview/)
- [Grafana Docs](https://grafana.com/docs/grafana/latest/)

---

## 📜 License

This project is licensed under the MIT License.

---

## 📑 Scripts

The `scripts/` directory contains utility scripts for testing and monitoring:

- `calls.sh` — Bash script to send test prediction requests to the serving API. Supports random or user-specified input and measures response time.
- `check_events.sh` — Bash script to check if prediction events have been indexed in Elasticsearch. Useful for verifying the event pipeline.

Usage examples are provided in the relevant sections above.

---

## ✍️ Author & Contributions

- Matheus Villela Torres
- email: matheusvt@gmail.com

---