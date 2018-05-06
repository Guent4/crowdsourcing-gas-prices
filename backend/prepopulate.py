import datetime
import os
import random
import shutil
import sys
import numpy as np

from django.utils import timezone
from geopy import units


def get_bounding_box(latitude, longitude, distancekm):
    rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distancekm)) * 2
    return latitude - rough_distance, latitude + rough_distance, longitude - rough_distance, longitude + rough_distance


def populate_database(num_locations, distance_range):
    random.seed(42)

    # delete all rows
    Company.objects.all().delete()
    Image.objects.all().delete()
    Station.objects.all().delete()
    Upload.objects.all().delete()

    if os.path.exists("media"):
        shutil.rmtree("media")

    # Some constants
    LATITUDE = 42.442445
    LONGITUDE = -76.485146
    PRICE_MIN = 2.0
    PRICE_MAX = 2.5
    COMPANIES = ["exxon", "mobil", "shell", "sunoco", "kwikfill", "bp", "chevron", "speedway", "wawa"]

    # So we can batch create
    uploads = []

    latitude_min, latitude_max, longitude_min, longitude_max = get_bounding_box(LATITUDE, LONGITUDE, distance_range)
    print(num_locations)
    for i in range(num_locations):
        if i % 10 == 0:
            print i

        companyname = random.choice(COMPANIES)
        latitude = random.uniform(latitude_min, latitude_max)
        longitude = random.uniform(longitude_min, longitude_max)
        price = round(random.uniform(PRICE_MIN, PRICE_MAX), 2)

        # pick random company
        company, _ = Company.objects.get_or_create(
            companyname=companyname
        )

        # use the same image for etsting
        # sample_image_path = os.path.join('prepopulate_data', 'prepopulate_sign.jpg')
        # image = Image()
        # image.imagefield.save('prepopulate_sign.jpg', File(open(sample_image_path, 'rb')))

        # create random station location
        station, _ = Station.objects.get_or_create(
            company=company,
            latitude=latitude,
            longitude=longitude
        )

        num_points = 5
        # num_points = random.randint(2, 5)
        day_deltas = sorted(random.sample(range(-6, 0), num_points))

        price_deltas = np.round(np.random.uniform(low=-0.1, high=0.1, size=(num_points,)), 2)

        for i in range(num_points):
            price += price_deltas[i]
            price = round(price, 2)
            uploads.append(Upload(
                latitude=latitude,
                longitude=longitude,
                timestamp=timezone.now() + datetime.timedelta(days=day_deltas[i]),
                station=station,
                price=price
            ))

    # Batch create
    Upload.objects.bulk_create(uploads)


# Start execution here!
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

    import django
    django.setup()
    from app.models import Company, Image, Station, Upload

    if len(sys.argv) == 1:
        num_locations = 400
        distance_range = 100
    else:
        num_locations = int(sys.argv[1])
        distance_range = int(sys.argv[2])
    populate_database(num_locations, distance_range)
