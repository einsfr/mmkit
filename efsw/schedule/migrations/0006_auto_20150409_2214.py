# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0005_auto_20150409_2207'),
    ]

    operations = [
        migrations.AddField(
            model_name='programposition',
            name='locked',
            field=models.BooleanField(verbose_name='заблокировано', default=False),
        ),
        migrations.AlterField(
            model_name='programposition',
            name='program',
            field=models.ForeignKey(to='schedule.Program', null=True, related_name='lineup_positions'),
        ),
    ]
