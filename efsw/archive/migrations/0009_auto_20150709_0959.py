# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
        ('archive', '0008_auto_20150708_2336'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemFileLocation',
            fields=[
                ('id', models.OneToOneField(serialize=False, to='common.FileStorageObject', primary_key=True)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ItemMetaLocation',
            fields=[
                ('id', models.OneToOneField(serialize=False, to='common.MetaStorageObject', primary_key=True)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.RemoveField(
            model_name='item',
            name='file_storage_objects',
        ),
        migrations.RemoveField(
            model_name='item',
            name='meta_storage_objects',
        ),
        migrations.AddField(
            model_name='itemmetalocation',
            name='item_id',
            field=models.ForeignKey(to='archive.Item', related_name='meta_locations'),
        ),
        migrations.AddField(
            model_name='itemfilelocation',
            name='item',
            field=models.ForeignKey(to='archive.Item', related_name='file_locations'),
        ),
    ]
