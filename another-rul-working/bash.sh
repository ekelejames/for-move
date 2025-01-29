docker logs <container_name_or_id>

# to filter the logs
docker logs <container_name_or_id> | grep "DEBUG"

# locate the logs file
# Navigating to the log directory:
# Default Kafka log directories include:
  /var/log/kafka
  /opt/kafka/logs
  Check your log4j.properties configuration for the exact file paths if customized.

tail -f /var/log/kafka/server.log
# mount the logs dir from the container to your host to be able to tail the logs from local computer

# append logs into a kafka topic
# edit the log4j.properties file

log4j.appender.KAFKA_LOG=org.apache.log4j.RollingFileAppender
log4j.appender.KAFKA_LOG.File=/var/log/kafka/kafka-logs.log
log4j.appender.KAFKA_LOG.layout=org.apache.log4j.PatternLayout
log4j.appender.KAFKA_LOG.layout.ConversionPattern=%d{ISO8601} [%t] %-5p %c - %m%n

# Add Kafka Appender to a topic
log4j.appender.KAFKA_TOPIC=org.apache.kafka.log4jappender.KafkaLog4jAppender
log4j.appender.KAFKA_TOPIC.topic=kafka-logs
log4j.appender.KAFKA_TOPIC.bootstrap.servers=localhost:9092
log4j.appender.KAFKA_TOPIC.layout=org.apache.log4j.PatternLayout
log4j.appender.KAFKA_TOPIC.layout.ConversionPattern=%d{ISO8601} [%t] %-5p %c - %m%n

# Attach appender to rootLogger
log4j.rootLogger=INFO, CONSOLE, KAFKA_LOG, KAFKA_TOPIC





### 
how can we use proxy in front to url in kafka connector