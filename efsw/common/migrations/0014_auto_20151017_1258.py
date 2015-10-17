# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0013_remove_conversation_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversation',
            name='participants',
            field=django.contrib.postgres.fields.ArrayField(size=None, verbose_name='участники разговора', base_field=models.IntegerField(), db_index=True),
        ),
    ]
