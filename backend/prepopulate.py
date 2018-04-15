import os, shutil
import sys
import json
from django.conf import settings
from django.core.files import File
from django.contrib.staticfiles.storage import staticfiles_storage
from datetime import datetime, timedelta
from django.utils import timezone
import pytz

import random

def populate_database():
    random.seed(42)

    # delete all rows
    Company.objects.all().delete()
    Image.objects.all().delete()
    Station.objects.all().delete()
    Upload.objects.all().delete()

    shutil.rmtree('media')

    canonical_lat = 42.4439617
    canonical_long = -76.5029963
    companies = ["exxon", "mobil", "shell", "sunoco"]
    fake_data_size = 100

    for i in range(fake_data_size):
        # pick random company
        company, _ = Company.objects.get_or_create(
            companyname=random.choice(companies)
        )

        # use the same image for etsting
        sample_image_path = os.path.join('prepopulate_data', 'prepopulate_sign.jpg')
        image = Image()
        image.imagefield.save('prepopulate_sign.jpg', File(open(sample_image_path, 'rb')))

        # create random station location
        flt = float(random.randint(-50,50))
        dec_lat = random.random()/100
        dec_lon = random.random()/100

        station, _ = Station.objects.get_or_create(
            company = company,
            latitude = canonical_lat + dec_lat,
            longitude = canonical_long + dec_lon
        )

        Upload.objects.get_or_create(
            latitude = canonical_lat + dec_lat,
            longitude = canonical_long + dec_lon,
            timestamp = timezone.now() + timedelta(days=random.randint(-5, 5)),
            station = station,  
            price = round(random.uniform(0, 5), 2),
            image = image
        )


# Start execution here!
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.local_settings')

    import django
    django.setup()
    from app.models import Company, Image, Station, Upload
    populate_database()
