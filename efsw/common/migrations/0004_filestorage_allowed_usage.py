# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0003_auto_20150709_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='filestorage',
            name='allowed_usage',
            field=django.contrib.postgres.fields.ArrayField(size=None, default=['archive'], base_field=models.CharField(max_length=16)),
            preserve_default=False,
        ),
    ]
