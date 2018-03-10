import os
import sys
import json
from django.conf import settings

def populate_database():
    # delete all rows
    Company.objects.all().delete()
    Image.objects.all().delete()
    Station.objects.all().delete()
    Upload.objects.all().delete()

    company, _ = Company.objects.get_or_create(
        companyname="exxon"
    )
    sample_image_path = os.path.join(settings.STATIC_ROOT, 'prepopulate_sign.jpg')
    image, _ = Image.imagefield(sample_image_path, f.read())
    station, _ = Station.objects.get_or_create(
        companyid = company.companyid,
        latitude = 14.10618,
        longitude = -44.78551
    )
    Upload.objects.get_or_create(
        latitude = -27.83406,
        longitude = 137.13269,
        stationid = station.stationid,  
        price = "1.99",
        imageid = image.imageid
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
