# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0010_auto_20150413_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programposition',
            name='program',
            field=models.ForeignKey(null=True, to='schedule.Program', related_name='lineup_positions', blank=True),
        ),
    ]
