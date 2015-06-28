# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConversionProcess',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('conv_id', models.UUIDField(editable=False, unique=True)),
                ('pid', models.PositiveIntegerField(editable=False)),
            ],
        ),
    ]
