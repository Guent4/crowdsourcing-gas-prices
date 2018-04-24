import datetime
import os
import shutil
import sys

import django
from django.core.files import File


def populate_database():
    # delete all rows
    Company.objects.all().delete()
    Image.objects.all().delete()
    Station.objects.all().delete()
    Upload.objects.all().delete()

    if os.path.exists("media"):
        shutil.rmtree("media")

    # company, _ = Company.objects.get_or_create(
    #     companyname="exxon"
    # )
    # sample_image_path = os.path.join('prepopulate_data', 'prepopulate_sign.jpg')
    # image = Image()
    # image.imagefield.save('prepopulate_sign.jpg', File(open(sample_image_path, 'rb')))
    #
    # station, _ = Station.objects.get_or_create(
    #     company = company,
    #     latitude = 14.10618,
    #     longitude = -44.78551
    # )
    #
    # Upload.objects.get_or_create(
    #     latitude = 14.10618,
    #     longitude = -44.78551,
    #     timestamp = datetime.datetime.now(),
    #     station = station,
    #     price = "1.99",
    #     image = image
    # )


# Start execution here!
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edge.settings')

    django.setup()
    from app.models import Company, Image, Station, Upload
    populate_database()
