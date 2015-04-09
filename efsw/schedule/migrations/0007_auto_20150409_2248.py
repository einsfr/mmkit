# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0006_auto_20150409_2214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lineup',
            name='active',
            field=models.BooleanField(verbose_name='используется', default=False),
        ),
        migrations.AlterField(
            model_name='lineup',
            name='active_until',
            field=models.DateField(verbose_name='используется до', null=True),
        ),
    ]
