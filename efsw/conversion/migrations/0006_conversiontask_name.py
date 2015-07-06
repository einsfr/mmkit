# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conversion', '0005_auto_20150701_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversiontask',
            name='name',
            field=models.CharField(max_length=255, default='название'),
            preserve_default=False,
        ),
    ]
