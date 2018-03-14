# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render


# Helper methods
from geopy import units

from app.models import Upload


def get_bounding_box(latitude, longitude, distancekm):
    rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distancekm)) * 2
    return latitude - rough_distance, latitude + rough_distance, longitude - rough_distance, longitude + rough_distance


# Create your views here.
def index(request):
    print request.path
    return HttpResponse("Hello, world. You're at the edge index.")


def map(request):
    assert request.method == "GET"
    user_latitude = float(request.GET["latitude"])
    user_longitude = float(request.GET["longitude"])
    user_range = float(request.GET["range"])

    min_lat, max_lat, min_long, max_long = get_bounding_box(user_latitude, user_longitude, user_range)

    objs_within = Upload.objects.filter(
        latitude__range=(
            min_lat,
            max_lat
        ),
        longitude__range=(
            min_long,
            max_long
        )
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