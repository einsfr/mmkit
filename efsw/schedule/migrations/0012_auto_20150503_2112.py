# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0011_auto_20150421_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineup',
            name='active_since',
            field=models.DateField(verbose_name='используется с', null=True),
        ),
        migrations.AlterField(
            model_name='lineup',
            name='channel',
            field=models.ForeignKey(to='schedule.Channel', related_name='lineups', verbose_name='канал'),
        ),
        migrations.AlterField(
            model_name='program',
            name='color',
            field=models.CharField(max_length=7, default='#ffffff', verbose_name='цвет фона'),
        ),
    ]
