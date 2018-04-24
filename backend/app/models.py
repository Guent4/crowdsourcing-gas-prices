# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models


# Create your models here.
class Company(models.Model):
    companyid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    companyname = models.CharField(max_length=200)


class Image(models.Model):
    imageid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    imagefield = models.ImageField()


class Station(models.Model):
    stationid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)


class Upload(models.Model):
    uploadid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    station = models.ForeignKey(
        Station,
        on_delete=models.CASCADE)
    price = models.CharField(max_length=10)
    image = models.ForeignKey(
        'Image',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )