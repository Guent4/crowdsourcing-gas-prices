# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse

from geopy import units
from django.core import serializers
from models import Company, Image, Station, Upload

def index(request):
    return JsonResponse({"message": "This is just the index page"})

def map(request):
    user_latitude = float(request.GET['latitude'])
    user_longitude = float(request.GET['longitude'])

    distance_range = 30
    rough_distance = units.degrees(arcminutes=units.nautical(kilometers=distance_range)) * 2
    objs_within = Upload.objects.filter(
        latitude__range=(
            user_latitude - rough_distance,
            user_latitude + rough_distance
        ),
        longitude__range=(
            user_longitude - rough_distance,
            user_longitude + rough_distance
        )
    ).select_related('stationid__companyid')
    resp = []
    for o in objs_within:
        d = {
            'latitude': o.latitude,
            'longitude': o.longitude,
            'price': o.price,
            'timestamp': o.timestamp,
            'companyname': o.stationid.companyid.companyname
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

def edge_update(request):
    return JsonResponse({"message": "e"})