#!/usr/bin/env python
import sys, os
from pprint import pprint

# Import module for testing
import weatherflow.api

# Define testing parameters
public_api_key = '20c70eae-e62f-4d3b-b3a4-8586e90f3ac8'
test_station = 690
test_device = 80810

if __name__ == "__main__":
    testrest = weatherflow.api.Rest(api_key=public_api_key, debug=False)
    # so = testrest.getStationObservation(test_station)
    # pprint(so)

    do = testrest.get_device_observations(test_device)

    pprint(do)
