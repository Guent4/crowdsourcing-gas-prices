import base64
import json
import sys
import time
import urllib

import datetime
import requests
import subprocess
from django.utils import timezone

EDGE_URL = "http://ec2-18-191-6-17.us-east-2.compute.amazonaws.com"

LATITUDE = 42.442445
LONGITUDE = -76.485146
RANGE = 20          # km

def evaluate_map_scarce():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "range": RANGE
    }

    repeat = 10
    minimum = float('inf')
    maximum = 0
    avg = 0

    for i in range(repeat):
        time_start = time.time()
        r = requests.get(url="{}/map".format(EDGE_URL), params=urllib.urlencode(params))
        duration = round(time.time() - time_start, 4)
        data = json.loads(r.content)["data"]
        assert len(data) == 5

        minimum = min(minimum, duration)
        maximum = max(maximum, duration)
        avg += duration

    avg /= float(repeat)

    print("map_scarce\tavg:{}\tmin:{}\tmax:{}".format(avg, minimum, maximum))



def evaluate_map_dense():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "range": RANGE
    }

    repeat = 10
    minimum = float('inf')
    maximum = 0
    avg = 0

    for i in range(repeat):
        time_start = time.time()
        r = requests.get(url="{}/map".format(EDGE_URL), params=urllib.urlencode(params))
        duration = round(time.time() - time_start, 4)
        data = json.loads(r.content)["data"]
        assert len(data) == 200

        minimum = min(minimum, duration)
        maximum = max(maximum, duration)
        avg += duration

    avg /= float(repeat)

    print("map_dense\tavg:{}\tmin:{}\tmax:{}".format(avg, minimum, maximum))


def evaluate_upload(image_path):
    data = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "timestamp": datetime.datetime.now().isoformat(),
        "price": 2.48,
        "companyname": "exxon",
        "image": base64.b64encode(open(image_path, "rb").read())
    }

    repeat = 10
    minimum = float('inf')
    maximum = 0
    avg = 0

    for i in range(repeat):
        time_start = time.time()
        r = requests.post(url="{}/upload_gas_price".format(EDGE_URL), json=data)
        duration = round(time.time() - time_start, 4)

        message = json.loads(r.content)["message"]
        assert message == "success"

        minimum = min(minimum, duration)
        maximum = max(maximum, duration)
        avg += duration

    avg /= float(repeat)

    print("upload\tavg:{}\tmin:{}\tmax:{}".format(avg, minimum, maximum))


def evaluate_sync():

    repeat = 3
    minimum = float('inf')
    maximum = 0
    avg = 0

    for i in range(repeat):
        time_start = time.time()
        r = requests.get(url="{}/initiate_sync".format(EDGE_URL))
        duration = round(time.time() - time_start, 4)
        print r.content
        message = json.loads(r.content)["message"]
        assert message == "success"

        minimum = min(minimum, duration)
        maximum = max(maximum, duration)
        avg += duration

    avg /= float(repeat)

    print("initiate_sync\tavg:{}\tmin:{}\tmax:{}".format(avg, minimum, maximum))

def evaluate_cache():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "companyname": "exxon"
    }

    time_start = time.time()
    r = requests.get(url="{}/historical".format(EDGE_URL), params=params)
    duration = round(time.time() - time_start, 4)
    print("uncached: {}".format(duration))

    time_start = time.time()
    r = requests.get(url="{}/historical".format(EDGE_URL), params=params)
    duration = round(time.time() - time_start, 4)
    print("cached: {}".format(duration))

if __name__ == "__main__":
    for _ in range(1 if len(sys.argv) <= 2 else int(sys.argv[2])):
        if sys.argv[1] == "map_scarce":
            evaluate_map_scarce()
        elif sys.argv[1] == "map_dense":
            evaluate_map_dense()
        elif sys.argv[1] == "upload_unmodified":
            evaluate_upload("unmodified.jpg")
        elif sys.argv[1] == "upload_modified":
            evaluate_upload("modified.jpg")
        elif sys.argv[1] == "initiate_sync":
            evaluate_sync()
        elif sys.argv[1] == "cache":
            evaluate_cache()
        else:
            raise NotImplementedError