import base64
import json
import sys
import time
import urllib

import datetime
import requests
from django.utils import timezone

EDGE_URL = "https://wonderful-elephant-52.localtunnel.me"

LATITUDE = 42.442445
LONGITUDE = -76.485146
RANGE = 20          # km


def evaluate_map_scarce():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "range": RANGE
    }

    time_start = time.time()
    r = requests.get(url="{}/map".format(EDGE_URL), params=urllib.urlencode(params))
    duration = round(time.time() - time_start, 4)

    data = json.loads(r.content)["data"]
    assert len(data) == 5

    print("map_scarce\t{}".format(duration))


def evaluate_map_dense():
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "range": RANGE
    }

    time_start = time.time()
    r = requests.get(url="{}/map".format(EDGE_URL), params=urllib.urlencode(params))
    duration = round(time.time() - time_start, 4)

    data = json.loads(r.content)["data"]
    assert len(data) == 200

    print("map_dense\t{}".format(duration))


def evaluate_upload(image_path):
    data = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "timestamp": datetime.datetime.now().isoformat(),
        "price": 2.48,
        "companyname": "exxon",
        "image": base64.b64encode(open(image_path, "rb").read())
    }

    time_start = time.time()
    r = requests.post(url="{}/upload_gas_price".format(EDGE_URL), json=data)
    duration = round(time.time() - time_start, 4)

    message = json.loads(r.content)["message"]
    assert message == "success"

    print("upload\t{}".format(duration))


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
        else:
            raise NotImplementedError
