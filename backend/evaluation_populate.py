import os
import random
import shutil
import sys

import django
from django.utils import timezone
from geopy import units
import datetime

LATITUDE = 42.442445
LONGITUDE = -76.485146
RANGE = 20          # km
PRICE_MIN = 2.0
PRICE_MAX = 2.5
COMPANIES = ["exxon", "mobil", "shell", "sunoco", "kwikfill", "bp", "chevron", "speedway", "wawa"]

def wipe_everything():
    # delete all rows
    Company.objects.all().delete()
    Image.objects.all().delete()
    Station.objects.all().delete()
    Upload.objects.all().delete()

    if os.path.exists("media"):
        shutil.rmtree("media")

def get_bounding_box(latitude, longitude, distancekm):
    rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distancekm)) * 2
    return latitude - rough_distance, latitude + rough_distance, longitude - rough_distance, longitude + rough_distance


def populate_map_with_density(num_stations, rng):
    # delete all rows
    Company.objects.all().delete()
    Image.objects.all().delete()
    Station.objects.all().delete()
    Upload.objects.all().delete()

    if os.path.exists("media"):
        shutil.rmtree("media")

    # Used for location randomization
    latitude_min, latitude_max, longitude_min, longitude_max = get_bounding_box(LATITUDE, LONGITUDE, rng)

    uploads = []
    for _ in range(num_stations):
        companyname = random.choice(COMPANIES)
        latitude = random.uniform(latitude_min, latitude_max)
        longitude = random.uniform(longitude_min, longitude_max)
        price = round(random.uniform(PRICE_MIN, PRICE_MAX), 2)

        company, _ = Company.objects.get_or_create(
            companyname=companyname
        )

        station, _ = Station.objects.get_or_create(
            company=company,
            latitude=latitude,
            longitude=longitude
        )

        uploads.append(Upload(
            latitude=latitude,
            longitude=longitude,
            timestamp=timezone.now(),
            station=station,
            price=price
        ))

    # Bulk create is much faster for larger amounts of data
    Upload.objects.bulk_create(uploads)


def populate_map_with_extra_point():
    companyname = "exxon"
    latitude = LATITUDE
    longitude = LONGITUDE
    price = 1.73

    company, _ = Company.objects.get_or_create(
        companyname=companyname
    )

    station, _ = Station.objects.get_or_create(
        company=company,
        latitude=latitude,
        longitude=longitude
    )

    Upload.objects.get_or_create(
        latitude=latitude,
        longitude=longitude,
        timestamp=timezone.now(),
        station=station,
        price=price
    )

def populate_map_with_historical():
    wipe_everything()

    companyname = "exxon"
    latitude = LATITUDE
    longitude = LONGITUDE

    company, _ = Company.objects.get_or_create(
        companyname=companyname
    )

    station, _ = Station.objects.get_or_create(
        company=company,
        latitude=latitude,
        longitude=longitude
    )

    Upload.objects.get_or_create(
        latitude=latitude,
        longitude=longitude,
        timestamp=timezone.now() + datetime.timedelta(days=-1),
        station=station,
        price=1.71
    )

    Upload.objects.get_or_create(
        latitude=latitude,
        longitude=longitude,
        timestamp=timezone.now(),
        station=station,
        price=1.73
    )

# Start execution here!
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

    django.setup()
    from app.models import Company, Image, Station, Upload
    if sys.argv[1] == "map_scarce":
        pass
    elif sys.argv[1] == "map_dense":
        pass
    elif sys.argv[1] == "upload_unmodified" or sys.argv[1] == "upload_modified":
        pass
    elif sys.argv[1] == "initiate_sync":
        populate_map_with_density(2000, 1000)
    elif sys.argv[1] == "cache":
        populate_map_with_historical()
    else:
        raise NotImplemented(sys.argv[1])
