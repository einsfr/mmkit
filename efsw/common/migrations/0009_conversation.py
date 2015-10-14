# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0008_auto_20151014_0831'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.UUIDField(primary_key=True, editable=False, serialize=False, default=uuid.uuid4)),
                ('updated', models.DateTimeField(editable=False, verbose_name='последнее обновление')),
                ('participants', django.contrib.postgres.fields.ArrayField(base_field=models.PositiveIntegerField(), size=None, verbose_name='участники разговора')),
                ('conv_type', models.IntegerField(editable=False, choices=[(0, 'диалог')], verbose_name='тип разговора')),
            ],
            options={
                'verbose_name_plural': 'разговоры',
                'verbose_name': 'разговор',
            },
        ),
    ]
