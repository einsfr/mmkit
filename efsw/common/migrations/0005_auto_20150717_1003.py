# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import django.contrib.postgres.fields.hstore
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0004_filestorage_allowed_usage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='filestorage',
            name='access_protocols',
            field=django.contrib.postgres.fields.hstore.HStoreField(default={}, blank=True),
        ),
        migrations.AlterField(
            model_name='filestorage',
            name='allowed_usage',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=16), default=[], blank=True, size=None),
        ),
        migrations.AlterField(
            model_name='filestorage',
            name='base_dir',
            field=models.CharField(max_length=255, unique=True, verbose_name='корневая директория'),
        ),
        migrations.AlterField(
            model_name='filestorage',
            name='id',
            field=models.UUIDField(serialize=False, default=uuid.uuid4, primary_key=True),
        ),
        migrations.AlterField(
            model_name='filestorageobject',
            name='path',
            field=models.CharField(max_length=255, unique=True, verbose_name='путь к объекту'),
        ),
    ]
