# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse

def index(request):
    return JsonResponse({"message": "This is just the index page"})

def map(request):
    return JsonResponse({"message": "n"})

def company_mapping(request):
    return JsonResponse({"message": "c"})

def edge_update(request):
    return JsonResponse({"message": "e"})