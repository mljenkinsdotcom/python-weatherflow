#!/usr/bin/env python
from pprint import pprint

# Import module for testing
import weatherflow.api

# Define testing parameters
public_api_key = '20c70eae-e62f-4d3b-b3a4-8586e90f3ac8'
test_station = 690
test_device = 80810

if __name__ == '__main__':
    testrest = weatherflow.api.Rest(api_key=public_api_key, debug=False)
    so = testrest.get_station_observation(test_station)
    print('Station observation:')
    pprint(so)
    print()

    do = testrest.get_device_observations(test_device)
    print('Device observations:')
    pprint(do)
    print()
