# Communication/Streaming Service

This folder contains configuration and persistent data for the streaming stack:

- **Kafka**: Handles event streaming between services.
- **Kafka Connect**: Connects Kafka topics to Elasticsearch for event storage.

All configuration files and persistent data are stored in this folder and mounted as volumes in the respective containers.
