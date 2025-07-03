flowchart TD
    U["User/API Client"]
    S["FastAPI Model Serving\n(serving/app.py)"]
    K["Kafka Broker"]
    ST["Streaming Service\n(communication/streaming.py)"]
    MLF["MLflow Tracking Server"]
    MIN["MinIO S3 Storage"]
    PR["Prometheus"]
    GR["Grafana"]
    ES["Elasticsearch"]

    U -->|"HTTP Predict Request"| S
    S -- "Load Model" --> MLF
    S -- "Save Artifacts" --> MIN
    S -- "Send Prediction Event" --> K
    S -- "Metrics" --> PR
    S -- "Log Events" --> ES
    K -- "Stream Events" --> ST
    ST -- "Index Events" --> ES
    PR -- "Metrics Data" --> GR
    ES -- "Monitoring Data" --> GR
    GR -- "Dashboards" --> U
    MLF -- "Model Metadata" --> S
    MIN -- "Model Artifacts" --> S

    classDef service stroke:#333,stroke-width:2px;
    class S,ST,MLF,MIN,PR,GR,ES,K service;