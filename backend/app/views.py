# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
import json

from geopy import units
from django.core import serializers
from models import Company, Image, Station, Upload
import uuid
import StringIO
import dateutil.parser
import base64
from django.core.files import File


def index(request):
    return JsonResponse({"message": "This is just the index page"})

def get_bounding_box(latitude, longitude, distancekm):
    rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distancekm)) * 2
    return (latitude - rough_distance, latitude + rough_distance, longitude - rough_distance, longitude + rough_distance)

def map(request):
    user_latitude = float(request.GET['latitude'])
    user_longitude = float(request.GET['longitude'])

    distance_range = 30
    min_latitude, max_latitude, min_longitude, max_longitude = get_bounding_box(user_latitude, user_longitude, distance_range)
    
    objs_within = Upload.objects.filter(
        latitude__range=(
            min_latitude,
            max_latitude
        ),
        longitude__range=(
            min_longitude,
            max_longitude
        )
    ).select_related('stationid__companyid')
    resp = []
    for o in objs_within:
        d = {
            'latitude': o.latitude,
            'longitude': o.longitude,
            'price': o.price,
            'timestamp': o.timestamp,
            'companyname': o.station.company.companyname
        }
        resp.append(d)
    return JsonResponse(resp, safe=False)

def company_mapping(request):
    companies = Company.objects.all()
    resp = []
    for c in companies:
        comp_dict = {}
        comp_dict['companyid'] = c.companyid
        comp_dict['companyname'] = c.companyname
        resp.append(comp_dict)

    return JsonResponse(resp, safe=False)

from django.views.decorators.csrf import csrf_exempt
# remove when deploy
@csrf_exempt
def edge_update(request):
     # or data[] if using jquery
    edge_data_list = json.loads(request.body)["data"]
    formatted_data = []
    # d = request.data

    for upload in edge_data_list:
        upload_latitude = float(upload["latitude"])
        upload_longitude = float(upload["longitude"])
        company_in_db = Company.objects.filter(companyname = upload["companyname"])
        if not company_in_db.exists():
            # if it is a new company, update db
            company, _ = Company.objects.get_or_create(
                companyname=upload["companyname"]
            )
        else:
            company = company_in_db[0]

        distance_range = 0.05 # a gas station in 50 meters
        min_latitude, max_latitude, min_longitude, max_longitude = get_bounding_box(upload_latitude, upload_longitude, distance_range)
        stations_in_db = Station.objects.filter(
            company=company, 
            latitude__range=(
                min_latitude,
                max_latitude
            ),
            longitude__range=(
                min_longitude,
                max_longitude
            )
        )
        if not stations_in_db.exists():
            # if there isn't a previously logged station within 50 meters of the same company, add new station
            station, _ = Station.objects.get_or_create(
                company=company,
                latitude=upload["latitude"],
                longitude=upload["longitude"]
            )
        else:
            # there is a station within 50 meters
            station = stations_in_db[0]
        
        cleaned_timestamp = dateutil.parser.parse(upload["timestamp"])

        potential_new_upload = Upload(
            timestamp=cleaned_timestamp,
            latitude=upload["latitude"],
            longitude=upload["longitude"],
            station=station,
            price=upload["price"]
        )
        uploads_in_db = Upload.objects.filter(
            timestamp=potential_new_upload.timestamp,
            latitude=potential_new_upload.latitude,
            longitude=potential_new_upload.longitude,
            station=potential_new_upload.station,
            price=potential_new_upload.price
        )
        # print cleaned_timestamp
        # print Upload.objects.all()[0].timestamp
        # print len(Upload.objects.filter(timestamp=cleaned_timestamp))
        if not uploads_in_db.exists():
            # decode base64 image and store into db
            image_str = upload["image"]
            # print len(image_str)
            image_str_file = StringIO.StringIO()
            image_str_file.write(base64.decodestring(image_str))
            image = Image()
            image.imagefield.save('{}.jpg'.format(uuid.uuid4()), File(image_str_file))
            potential_new_upload.image = image

            formatted_data.append(potential_new_upload)

    old_count = Upload.objects.count()
    Upload.objects.bulk_create(formatted_data)
    new_count = Upload.objects.count()
    
    if old_count != new_count:
        message = "updated db"
    else:
        message = "db already had data"


    return JsonResponse({"message": message})