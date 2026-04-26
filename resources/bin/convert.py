#!/usr/bin/env python3
import sys
import json
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO

# Function to read YAML content from a file
def read_yaml_file(file_path):
    with open(file_path, 'r') as file:
        yaml = YAML()
        return yaml.load(file)

# Function to write JSON content to a file
def write_json_file(data):
    print(json.dumps(data, indent=4))

# Function to convert YAML to JSON
def convert_yaml_to_json(yaml_file_path):
    yaml_data = read_yaml_file(yaml_file_path)
    write_json_file(yaml_data)

# Example usage
if __name__ == "__main__":
    convert_yaml_to_json(sys.argv[1])

