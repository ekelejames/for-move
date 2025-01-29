from uuid import uuid4
import random
import json
import time

from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient, SchemaRegistryError
from confluent_kafka.schema_registry.json_schema import JSONSerializer

import yaml
import sys
from pathlib import Path
from string import Template
import requests
import argparse


def generate_message():
    epoch_time = int(time.time())

    data = {}

    epoch_time = int(time.time())
    captive = random.choice(["performance-gls"])
    shelf_list = {
        "performance-gls": ["1145", "167"]
    }

    data["process-time"] = epoch_time
    data["captive"] = captive
    data["shelf"] = random.choice(shelf_list[captive])
    data["load"] = random.choice(["ee-109", "er-122"])
    data["release"] = random.choice(["030300"])
    data["baseline-load"] = random.choice(["ab-347", "cd-245"])
    data["baseline-release"] = random.choice(["030300"])
    data["num-channels-before"] = random.choice([0, 64])
    data["num-channels-after"] = random.choice([0, 64])
    data["operation"] = random.choice(["add", "delete"])
    data["result"] = str(random.choice(["Healthy", "Unhealthy"]))
    data["reason"] = random.choice(["custom_reason1", "custom_reason2"])
    data["mean"] = round(random.uniform(1, 10), 2)
    data["stddev"] = round(random.uniform(0, 2), 2)
    data["min"] = round(random.uniform(0, 1), 2)
    data["max"] = round(random.uniform(10, 20), 2)
    data["percentile-50"] = round(random.uniform(5, 10), 2)
    data["percentile-90"] = round(random.uniform(7, 15), 2)
    data["percentile-99"] = round(random.uniform(10, 20), 2)

    return data


def delivery_report(err, msg):
    """
    Reports the success or failure of a message delivery.

    Args:
        err (KafkaError): The error that occurred or None on success.
        msg (Message): The message that was produced or failed.
    """
    if err is not None:
        print("Delivery failed for serviceBrokerStats record {}: {}".format(msg.key(), err))
        return


def main():
    parser = argparse.ArgumentParser(description="Sample Flat Schema Metric Producer")
    parser.add_argument("--sb_host", help="The hostname of the streambed server")
    parser.add_argument("--yaml_file", help="The path to the YAML file containing the configuration")
    parser.add_argument("--num_msg", help="Number of messages to produce")
    args = parser.parse_args()

    SB_HOST = args.sb_host
    YAML_FILE = args.yaml_file
    NUM_MSG = int(args.num_msg)

    with open(YAML_FILE, 'r') as file:
        yaml_input = Template(file.read()).substitute(HOSTNAME=SB_HOST)
        config = yaml.safe_load(yaml_input)

    # print config with indentation
    print(f"yaml_input: { yaml.dump(config, default_flow_style=False) }")

    KAFKA_TOPIC = config['kafka']['topic']

    print("Producing serviceBrokerStats records to topic {}. ^C to exit.".format(KAFKA_TOPIC))

    try:
        num_msg = 0
        while num_msg < NUM_MSG:
            record = generate_message()
            print(f"Produced the following message to {KAFKA_TOPIC}:\n{json.dumps(record, indent=2)}\n")

            url = f"http://{SB_HOST}:8082/v1/metrics/data"
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            message = {
                "metric-name": KAFKA_TOPIC,
                "message": record
            }

            response = requests.post(url, headers=headers, json=message)

            # Print the response status code and text
            print(response.status_code)
            print(response.text)
            time.sleep(0.1)
            num_msg += 1
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()



