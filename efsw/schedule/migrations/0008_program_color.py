# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0007_auto_20150409_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='color',
            field=models.CharField(max_length=7, default='ffffff', verbose_name='цвет фона'),
        ),
    ]
