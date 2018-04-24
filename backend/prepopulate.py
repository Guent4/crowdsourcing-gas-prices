import datetime
import os
import random
import shutil
import sys

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
        price = random.uniform(PRICE_MIN, PRICE_MAX)

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

        for _ in range(random.randint(2, 5)):
            uploads.append(Upload(
                latitude=latitude,
                longitude=longitude,
                timestamp=datetime.datetime.now() + datetime.timedelta(days=random.randint(-5, 0), hours=random.randint(-24, 0)),
                station=station,
                price=round(random.uniform(0, 5), 2)
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
    populate_database(int(sys.argv[1]), int(sys.argv[2]))
