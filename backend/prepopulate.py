import os
import sys
import json

def populate_database(data_files):
    # delete all rows
    Company.objects.all().delete()
    Company.objects.get_or_create(
        companyid="1",
        companyname="exxon"
    )

# Start execution here!
if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding("utf-8")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.local_settings')

    import django
    django.setup()
    from app.models import *
    populate_database()
