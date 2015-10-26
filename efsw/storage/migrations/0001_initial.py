# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields
import uuid
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileStorage',
            fields=[
                ('id', models.UUIDField(serialize=False, default=uuid.uuid4, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='имя')),
                ('base_dir', models.CharField(unique=True, max_length=255, verbose_name='корневая директория')),
                ('access_protocols', django.contrib.postgres.fields.hstore.HStoreField(blank=True, default={})),
                ('read_only', models.BooleanField(verbose_name='только для чтения', default=True)),
                ('allowed_usage', django.contrib.postgres.fields.ArrayField(size=None, blank=True, base_field=models.CharField(max_length=16), default=[])),
            ],
            options={
                'verbose_name': 'файловое хранилище',
                'verbose_name_plural': 'файловые хранилища',
            },
        ),
        migrations.CreateModel(
            name='FileStorageObject',
            fields=[
                ('id', models.UUIDField(serialize=False, default=uuid.uuid4, primary_key=True, editable=False)),
                ('path', models.CharField(unique=True, max_length=255, verbose_name='путь к объекту')),
                ('storage', models.ForeignKey(to='storage.FileStorage', related_name='stored_objects')),
            ],
            options={
                'verbose_name': 'объект в файловом хранилище',
                'verbose_name_plural': 'объекты в файловом хранилище',
            },
        ),
    ]
