# coding: utf-8

import os
import yaml
import json

from opencti import OpenCTI

# Load configuration
config = yaml.load(open(os.path.dirname(__file__) + '/../config.yml'))

# Export file
export_file = './exports/IntrusionSets.json'

# OpenCTI initialization
opencti = OpenCTI(config['opencti']['api_url'], config['opencti']['api_key'], config['opencti']['log_file'], config['opencti']['verbose'])

# Import the bundle
bundle = opencti.stix2_export_entity('report', '{ENTITY_ID}', 'full')

with open(export_file, 'w') as file:
    json.dump(bundle, file, indent=4)
