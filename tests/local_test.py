#!/usr/bin/env python
import sys, os, time
from pprint import pprint

# Import module for testing
import weatherflow.api

if __name__ == "__main__":
    testudp = weatherflow.api.Udp(debug=False)
    testudp.start()

    listen_seconds = 15
    for i in list(range(listen_seconds)):
        if testudp.new_data_available():
            data = testudp.get_latest_data()
            print(data)
        time.sleep(1)

    testudp.stop()

    print("Finished main function")
