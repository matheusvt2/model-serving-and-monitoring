# Scripts Folder

This folder contains utility scripts for testing and monitoring the ML pipeline:

- `calls.sh`: Sends test prediction requests to the serving API, supporting both random and user-specified input.
- `check_events.sh`: Checks if prediction events have been indexed in Elasticsearch, verifying the event pipeline.

Use these scripts to validate and monitor your end-to-end ML workflow.
