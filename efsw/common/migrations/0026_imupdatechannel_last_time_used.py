# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0025_auto_20151018_2200'),
    ]

    operations = [
        migrations.AddField(
            model_name='imupdatechannel',
            name='last_time_used',
            field=models.DateTimeField(default=datetime.datetime(2015, 10, 18, 19, 15, 16, 888824, tzinfo=utc), verbose_name='дата и время последнего обращения к каналу', editable=False),
            preserve_default=False,
        ),
    ]
