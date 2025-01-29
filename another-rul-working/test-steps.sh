# move files into broker container
docker cp testuser_1.properties kafka:/tmp/
docker cp testuser_2.properties kafka:/tmp/
docker cp consumer_1.properties kafka:/tmp/
docker cp consumer_2.properties kafka:/tmp/
docker cp admin.properties kafka:/tmp/

# create a topic. test-topic
docker exec -it kafka kafka-topics --bootstrap-server kafka:9092 --command-config /tmp/admin.properties --create --partitions 3 --replication-factor 1  --topic test-topic
docker exec -it kafka kafka-topics --bootstrap-server kafka:9092 --command-config /tmp/testuser_1.properties --create --partitions 3 --replication-factor 1  --topic test-topic-2

# haven't seen it in the audit. maybe when we create using a user

# create 2 users
docker exec -it kafka kafka-configs --bootstrap-server kafka:29092 --alter --add-config 'SCRAM-SHA-512=[password=testuser_1]' --entity-type users --entity-name testuser_1
docker exec -it kafka kafka-configs --bootstrap-server kafka:29092 --alter --add-config 'SCRAM-SHA-512=[password=testuser_2]' --entity-type users --entity-name testuser_2

# give acls to one user for the topic
docker exec -it kafka kafka-acls --bootstrap-server kafka:29092 --add  --allow-principal User:testuser_1  --operation ALL --topic test-topic

# produce to the topic using each user
docker exec -it kafka kafka-console-producer --bootstrap-server kafka:9092 --topic test-topic --producer.config /tmp/user_1.properties
docker exec -it kafka kafka-console-producer --bootstrap-server kafka:9092 --topic test-topic --producer.config /tmp/user_2.properties

# consume from the topic using each user
docker exec -it kafka kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic test-topic --consumer.config /tmp/consumer_1.properties --from-beginning

docker exec -it kafka kafka-console-consumer.sh --bootstrap-server kafka:9092 --topic test-topic --consumer.config /tmp/consumer_2.properties --from-beginning
# check the audit log events topic for audits


######################

docker cp kafka_audit_log_mongo_sink.json kafka-connect:/home/appuser

# create ACLs for the consumer group of the sink connector to be able to consume from the topic

## execute into it

docker exec -it kafka kafka-acls --bootstrap-server kafka:29092  --add --allow-principal User:admin --consumer --topic confluent-audit-log-events --group connect-connector1



# create the sink connector
docker exec -it kafka-connect bash
curl -X POST -H "Content-Type: application/json" --data @kafka_audit_log_mongo_sink.json http://localhost:8083/connectors


################## schema registry #################

docker exec -it schema-registry bash

curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" --data '{ "schema": "{\"type\":\"record\",\"name\":\"MyRecord\",\"fields\":[{\"name\":\"field1\",\"type\":\"string\"}]}" }' http://schema-registry:8085/subjects/james-test-8-value/versions

##### NOTE : Audit log does not log schema attachment to topic

### lets make the schema registry use a user
38




