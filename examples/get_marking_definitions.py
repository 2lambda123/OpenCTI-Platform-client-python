# coding: utf-8

from pycti import OpenCTIApiClient, MarkingDefinition

# Variables
api_url = 'https://demo.opencti.io'
api_token = 'ab3c02bb-2849-4223-be5d-8f61207b4b43'

# OpenCTI initialization
opencti_api_client = OpenCTIApiClient(api_url, api_token)

# Get all marking definitions
marking_definitions = opencti_api_client.marking_definition.list()

# Print
for marking_definition in marking_definitions:
    print('[' + marking_definition['definition_type'] + '] ' + marking_definition['definition'])
