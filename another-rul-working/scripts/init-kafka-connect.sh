#!/bin/bash

# Start Kafka Connect
/etc/confluent/docker/run &

# Wait for Kafka Connect listener
echo "Waiting for Kafka Connect to start listening on localhost"
while : ; do
  curl_status=$(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors)
  echo -e $(date) " Kafka Connect listener HTTP state: " $curl_status " (waiting for 200)"
  if [ $curl_status -eq 200 ] ; then
    break
  fi
  sleep 5 
done

# Register the PostgreSQL sink connector
#echo "Registering the PostgreSQL sink connector..."
#curl -X POST -H "Content-Type: application/json" --data @/streambed-sink-config/baseline-postgresql-sink-config.json http://localhost:8083/connectors

# Keep the container running
tail -f /dev/null


confluent-audit-log-events