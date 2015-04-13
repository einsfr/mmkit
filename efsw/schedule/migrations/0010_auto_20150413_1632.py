# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0009_auto_20150413_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineup',
            name='channel',
            field=models.ForeignKey(default=1, to='schedule.Channel', related_name='lineups'),
            preserve_default=False,
        ),
    ]
