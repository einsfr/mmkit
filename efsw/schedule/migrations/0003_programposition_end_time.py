# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0002_auto_20150408_1726'),
    ]

    operations = [
        migrations.AddField(
            model_name='programposition',
            name='end_time',
            field=models.TimeField(default='00:00:00', verbose_name='время окончания'),
            preserve_default=False,
        ),
    ]
