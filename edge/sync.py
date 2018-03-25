import base64
import os
import sys

import django
import requests


def sync():
    data = []
    for upload in Upload.objects.all():
        if upload.image is not None:
            with open(os.path.join("media", upload.image.imagefield), "rb") as image_file:
                image_str = base64.b64encode(image_file.read())
        else:
            image_str = ""

        datum = {
            "latitude": str(upload.latitude),
            "longitude": str(upload.longitude),
            "timestamp": upload.timestamp.isoformat(),
            "price": upload.price,
            "companyname": upload.station.company.companyname,
            "image": image_str
        }
        data.append(datum)

        print(upload.station.stationid)

    # requests.post(url=BACKEND_ENDPOINT, data=data)


# Start execution here!
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edge.settings')

    django.setup()
    from app.models import Upload
    sync()