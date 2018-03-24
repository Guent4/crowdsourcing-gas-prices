# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import StringIO
import base64
import json
import uuid

import dateutil.parser
from app.models import Upload, Company, Station, Image
from django.core.files import File
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from geopy import units


# Decorators
def valid_request_methods(methods):
    """
    Decorator for checking to make sure got the right HTTP method
    :param methods: List of acceptable HTTP methods
    :return: Decorator
    """
    def func_decorator(func):
        def func_wrapper(request):
            if request.method not in methods:
                return JsonResponse({"message": "Expected {}, but got {}".format(", ".join(methods), request.method)}, status=400)
            else:
                return func(request)
        return func_wrapper
    return func_decorator


# Helper methods
def get_bounding_box(latitude, longitude, distancekm):
    rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distancekm)) * 2
    return latitude - rough_distance, latitude + rough_distance, longitude - rough_distance, longitude + rough_distance


def get_station_from_lat_long_companyname(latitude, longitude, distancekm, companyname):
    # Check the company
    company_in_db = Company.objects.filter(companyname=companyname)
    if len(company_in_db) == 0:
        company, _ = Company.objects.get_or_create(comapnyname=companyname)
    else:
        company = company_in_db[0]

    # Check for station within 50m
    distance_range = distancekm
    min_lat, max_lat, min_long, max_long = get_bounding_box(latitude, longitude, distance_range)
    stations_in_db = Station.objects.filter(
        company=company,
        latitude__range=(min_lat, max_lat),
        longitude__range=(min_long, max_long)
    )
    if len(stations_in_db) == 0:
        station, _ = Station.objects.get_or_create(company=company, latitude=latitude,longitude=longitude)
    else:
        station = stations_in_db[0]

    return company, station


# Create your views here.
def index(request):
    print request.path
    return HttpResponse("Hello, world. You're at the edge index.")


@valid_request_methods(["GET"])
def map(request):
    user_latitude = float(request.GET["latitude"])
    user_longitude = float(request.GET["longitude"])
    user_range = float(request.GET["range"])

    min_lat, max_lat, min_long, max_long = get_bounding_box(user_latitude, user_longitude, user_range)

    objs_within = Upload.objects.filter(
        latitude__range=(min_lat, max_lat),
        longitude__range=(min_long, max_long)
    ).select_related("station__company")
    resp_dict = {}
    for o in objs_within:
        stationid = o.station.stationid
        if (stationid not in resp_dict) or (stationid in resp_dict and resp_dict[stationid]["timestamp"] < o.timestamp):
            resp_dict[stationid] = {
                "latitude": o.latitude,
                "longitude": o.longitude,
                "price": o.price,
                "timestamp": o.timestamp,
                "companyname": o.station.company.companyname
            }

    return JsonResponse(resp_dict.values(), safe=False)


@valid_request_methods(["GET"])
def company_mapping(request):
    resp = []
    for company in Company.objects.all():
        resp.append({"companyid": company.companyid, "companyname": company.companyname})

    return JsonResponse(resp, safe=False)


@csrf_exempt
@valid_request_methods(["POST"])
def upload_gas_price(request):
    data = json.loads(request.body)

    # Parse out the data
    latitude = float(data["latitude"])
    longitude = float(data["longitude"])
    timestamp = dateutil.parser.parse(data["timestamp"])
    price = float(data["price"])
    companyname = data["companyname"]
    image_str = data["image"]

    # Get (or insert) company and station
    company, station = get_station_from_lat_long_companyname(latitude, longitude, 0.05, companyname)

    # Deal with the image
    image_str_file = StringIO.StringIO()
    image_str_file.write(base64.decodestring(image_str))
    image = Image()
    image.imagefield.save('{}.jpg'.format(uuid.uuid4()), File(image_str_file))

    # Create the upload
    upload, _ = Upload.objects.get_or_create(
        latitude=latitude,
        longitude=longitude,
        timestamp=timestamp,
        station=station,
        price=price,
        image=image
    )

    # Update the GPS location of the gas station
    uploads_of_same_station = Upload.objects.filter(station=station)
    latitude_sum = 0
    longitude_sum = 0
    count = 0
    for upload in uploads_of_same_station:
        latitude_sum += upload.latitude
        longitude_sum += upload.longitude
        count += 1
    latitude_new = latitude_sum / count
    longitude_new = longitude_sum / count
    Station.objects.filter(pk=station.stationid).update(latitude=latitude_new, longitude=longitude_new)

    return JsonResponse({"message": "success"})

@csrf_exempt
@valid_request_methods(["POST"])
def backend_sync(request):
    data = json.loads(request.body)
    stations = data["stations"]
    uploads = data["uploads"]

    for s in stations:
        latitude = float(s["latitude"])
        longitude = float(s["longitude"])
        companyname = s["companyname"]

        # Get (or insert) company and station
        company, station = get_station_from_lat_long_companyname(latitude, longitude, 0.05, companyname)

    for u in uploads:
        latitude = float(u["latitude"])
        longitude = float(u["longitude"])
        timestamp = dateutil.parser.parse(u["timestamp"])
        companyname = u["companyname"]
        price = float(u["price"])

        # Get (or insert) company and station
        company, station = get_station_from_lat_long_companyname(latitude, longitude, 0.05, companyname)

        upload, _ = Upload.objects.get_or_create(
            latitude=latitude,
            longitude=longitude,
            timestamp=timestamp,
            station=station,
            price=price
        )

        return JsonResponse({"message": "success"})
