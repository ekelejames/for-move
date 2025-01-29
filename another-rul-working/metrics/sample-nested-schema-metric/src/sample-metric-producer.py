from uuid import uuid4
import random
import json
import time

import yaml
import sys
from pathlib import Path
import requests
import argparse


def generate_message(selected_directory):
    epoch_time = int(time.time())

    # read from the selected directory
    with open(selected_directory, "r") as file:
        raw_data = json.load(file)

    data = {}
    data["broker-stats"] = raw_data[0]["data"]

    epoch_time = int(time.time())
    captive = random.choice(["performance-gls"])
    shelf_list = {
        "performance-gls": ["1145", "167"]
    }
    context = {
        "captive": "performance-gls",
        "shelf": random.choice(shelf_list[captive]),
        "load": random.choice(["ee-109", "er-122"]),
        "release": random.choice(["030300"])

    }
    data["context"] = context
    
    context_state = {
        "num-channels": random.choice([0, 64]),
        "mcp-enrollment": random.choice([True, False]),
        "telemetry": [
            {
                "protocol": "TCP",
                "is-subscription-active": False
            }
        ]
    }
    data["context-state"] = context_state

    data["num-channels-before"] = random.choice([0, 64])
    data["num-channels-after"] = random.choice([0, 64])
    data["start-time"] = epoch_time
    data["elapsed-time"] = str(round(random.uniform(1, 10), 2))
    data["operation"] = random.choice(['add', 'delete'])

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
        yaml_input = file.read()
        config = yaml.safe_load(yaml_input)

    # print config with indentation
    print(f"yaml_input: { yaml.dump(config, default_flow_style=False) }")

    KAFKA_TOPIC = config['kafka']['topic']

    with open(f"{Path(__file__).parents[2]}/rls-declarative-push/src/service-broker-stats-paths.json", "r") as file:
        directories = json.load(file) 
    try:
        num_msg = 0
        while num_msg < NUM_MSG:
            selected_directory = random.choice(directories)
            record = generate_message(selected_directory)
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

    print(f"Declarative Push Producer finished producing {num_msg} messages")

if __name__ == '__main__':
    main()
