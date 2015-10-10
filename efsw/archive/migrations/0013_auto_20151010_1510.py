# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0012_auto_20150715_1513'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemfilelocation',
            name='file_object',
            field=models.OneToOneField(serialize=False, related_name='+', primary_key=True, to='common.FileStorageObject'),
        ),
        migrations.AlterField(
            model_name='itemlog',
            name='user',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+'),
        ),
    ]
