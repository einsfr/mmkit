# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0004_auto_20150409_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programposition',
            name='comment',
            field=models.CharField(blank=True, verbose_name='комментарий', max_length=32),
        ),
    ]
