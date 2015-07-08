# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
        ('archive', '0007_auto_20150529_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='file_storage_objects',
            field=models.ManyToManyField(related_name='+', to='common.FileStorageObject'),
        ),
        migrations.AddField(
            model_name='item',
            name='meta_storage_objects',
            field=models.ManyToManyField(related_name='+', to='common.MetaStorageObject'),
        ),
    ]
