# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0009_conversation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='participants',
            field=django.contrib.postgres.fields.ArrayField(size=None, base_field=models.PositiveIntegerField(), verbose_name='участники разговора', db_index=True),
        ),
        migrations.AlterField(
            model_name='conversation',
            name='updated',
            field=models.DateTimeField(db_index=True, verbose_name='последнее обновление', editable=False),
        ),
    ]
