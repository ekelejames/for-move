# Sample Nested Schema Metric

## Overview
This project demonstrates how to create a nested schema metric, register the schema in the schema registry, and produce messages to Kafka. The messages are then consumed by a Kafka Connect Sink and stored in a MongoDB database.

## Architecture
![Architecture Image](docs/architecture.jpg)

### schema registry
export SCHEMAHOST=localhost
#### Register Schema
```sh
curl -X 'POST' \
  "http://${SCHEMAHOST}:8082/v1/metrics/schema" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "metric-name": "sample_nested_schema_metric",
  "schema": '"$(cat schema/sample-nested-schema.json)"',
  "schema-type": "JSON"
}'
```

#### Query Schema
```sh
curl -X 'GET' \
  "http://${SCHEMAHOST}:8082/v1/metrics/schema" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "metric-name": "sample_nested_schema_metric"
}'
```

#### (Optional) Delete Schema
```sh
curl -X 'DELETE' \
  "http://${SCHEMAHOST}:8082/v1/metrics/schema" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "metric-name": "sample_nested_schema_metric"
}'
```
### Kafka Connect Sink to PostgreSQL
#### Create Kafka Connect Sink
```sh
docker exec -it kafka-connect bash
curl -X POST -H "Content-Type: application/json" --data "$(cat config/sample-sink-config.json)" http://localhost:8083/connectors
```
#### View the Metric Topic in Kafka Confluent Control Center
Navigate to http://{KAFKAHOST}:9021/ in your browser.
![Kafka Connect Image](docs/kafka_connect.jpg)

#### Query Kafka Connect Sink
```sh
docker exec -it kafka-connect bash
curl -X GET http://localhost:8083/connectors/sample-mongodb-sink-connector
```

#### (Optional) Delete Kafka Connect Sink
```sh
docker exec -it kafka-connect bash
curl -X DELETE http://localhost:8083/connectors/sample-mongodb-sink-connector
```

### Produce Messages to Kafka
```sh
source /nfs/projects/equinox/streambed/tools/streambed-venv/bin/activate
python src/sample-metric-producer.py --sb_host "$SCHEMAHOST" --yaml_file config/sample-streambed-config.yaml --num_msg 1
```
#### (Optional) Consume Messages from Kafka
```sh
source /nfs/projects/equinox/streambed/tools/streambed-venv/bin/activate
export KAFKAHOST=localhost
python /nfs/projects/equinox/streambed/git/marc-proto/streambed/src/streambed/utils/kafka/json-consumer.py "$KAFKAHOST" config/sample-streambed-config.yaml
```

### MongoDB
```sh
docker exec -it mongo-shell mongosh --host mongo -u root -p root
use streambed_database
show collections
db.sample_nested_collection.find().pretty()
db.sample_nested_collection.drop()
```

### MongoDB GUI (mongo-express)
Navigate to http://${MongoDBHOST}:8084 in your browser.
![MongoDB Image](docs/MongoDB.jpg)

### Baseline Comparison
```sh
curl -X 'POST' \
  "http://${SCHEMAHOST}:8082/v1/operations/baseline-compare" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "metric-name": "sample_nested_schema_metric",
  "database-config": {
    "database-type": "mongodb",
    "hostname": "mongo",
    "database-name": "streambed_database",
    "database-table-name": "sample_nested_collection",
    "db-username": "root",
    "db-password": "root"
  },
  "algorithm": "effect-size",
  "context-a": {
    "context": {
      "load": "ee-109",
      "shelf": "1145",
      "captive": "performance-gls",
      "release": "030300"
    }
  },
  "context-b": {
    "context": {
      "load": "er-122",
      "shelf": "1145",
      "captive": "performance-gls",
      "release": "030300"
    }
  },
  "metric": [
    "elapsed-time"
  ],
  "filter-on": {
    "operation": "add",
    "num-channels-before": 0,
    "num-channels-after": 64
  }
}'
```

# Health check
```sh
curl -X 'POST' \
  "http://${SCHEMAHOST}:8082/v1/operations/baseline-health-check" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "metric-name": "sample_nested_schema_metric",
  "database-config": {
    "database-type": "mongodb",
    "hostname": "mongo",
    "database-name": "streambed_database",
    "database-table-name": "sample_nested_collection",
    "db-username": "root",
    "db-password": "root"
  },
  "algorithm": "effect-size",
  "context-a": {
    "context": {
      "load": "ee-109",
      "shelf": "1145",
      "captive": "performance-gls",
      "release": "030300"
    }
  },
  "context-b": {
    "context": {
      "load": "er-122",
      "shelf": "1145",
      "captive": "performance-gls",
      "release": "030300"
    }
  },
  "metric": [
    "elapsed-time"
  ],
  "filter-on_keys": [
    "operation",
    "num-channels-before",
    "num-channels-after"
  ]
}'
```