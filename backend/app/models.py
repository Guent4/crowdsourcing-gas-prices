# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import uuid


# where to create models for db
class Company(models.Model):
    companyid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    companyname = models.CharField(max_length=200)
