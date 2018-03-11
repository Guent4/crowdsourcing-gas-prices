# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse

from models import Company, Image, Station, Upload

def index(request):
    return JsonResponse({"message": "This is just the index page"})

def map(request):
    return JsonResponse({"message": "n"})

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