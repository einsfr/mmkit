# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0013_auto_20151010_1510'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemfilelocation',
            name='file_object',
            field=models.ForeignKey(primary_key=True, related_name='+', to='common.FileStorageObject', serialize=False),
        ),
    ]
