# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0003_programposition_end_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineup',
            name='end_time',
            field=models.TimeField(default='06:00:00', verbose_name='время окончания эфирных суток'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='lineup',
            name='start_time',
            field=models.TimeField(default='06:00:00', verbose_name='время начала эфирных суток'),
            preserve_default=False,
        ),
    ]
