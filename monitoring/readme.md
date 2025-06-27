# Monitoring Folder

This folder contains all configuration and persistent data for the monitoring stack:

- **Prometheus**: Collects and stores metrics from the serving service and itself (see `prometheus.yml`).
- **Grafana**: Visualizes metrics and events; dashboards and persistent data are stored here (see `grafana/`).
- **Elasticsearch**: Stores prediction events and supports fast search and aggregation.

All dashboards, configuration files, and persistent data are stored here and mounted as volumes in the respective containers.
