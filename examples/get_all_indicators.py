# coding: utf-8

from pycti import OpenCTIApiClient

# Variables
api_url = 'https://demo.opencti.io'
api_token = 'bb4aca90-b98c-49ee-9582-7eac92b61b82'

# OpenCTI initialization
opencti_api_client = OpenCTIApiClient(api_url, api_token)

# Get all indicators
indicators = opencti_api_client.indicator.list(getAll=True)

# Print
for indicator in indicators:
    print('[' + indicator['pattern_type'] + '] ' + indicator['pattern'])