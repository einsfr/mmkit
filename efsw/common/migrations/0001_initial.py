# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import django.contrib.postgres.fields.hstore


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FileStorage',
            fields=[
                ('id', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='имя')),
                ('base_dir', models.CharField(max_length=255, verbose_name='корневая директория')),
                ('access_protocols', django.contrib.postgres.fields.hstore.HStoreField(editable=False)),
                ('read_only', models.BooleanField(default=True, verbose_name='только для чтения')),
            ],
            options={
                'verbose_name': 'файловое хранилище',
                'verbose_name_plural': 'файловые хранилища',
            },
        ),
        migrations.CreateModel(
            name='FileStorageObject',
            fields=[
                ('id', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('path', models.CharField(max_length=255, verbose_name='путь к объекту')),
                ('storage', models.ForeignKey(related_name='stored_objects', to='common.FileStorage')),
            ],
            options={
                'verbose_name': 'объект в файловом хранилище',
                'verbose_name_plural': 'объекты в файловом хранилище',
            },
        ),
        migrations.CreateModel(
            name='MetaStorage',
            fields=[
                ('id', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='имя')),
            ],
            options={
                'verbose_name': 'хранилище метаданных',
                'verbose_name_plural': 'хранилища метаданных',
            },
        ),
        migrations.CreateModel(
            name='MetaStorageObject',
            fields=[
                ('id', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('location', models.CharField(max_length=255, verbose_name='место хранения объекта')),
                ('storage', models.ForeignKey(related_name='stored_objects', to='common.MetaStorage')),
            ],
            options={
                'verbose_name': 'объект в хранилище метаданных',
                'verbose_name_plural': 'объекты в хранилище метаданных',
            },
        ),
    ]
