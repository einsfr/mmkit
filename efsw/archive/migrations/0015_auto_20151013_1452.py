# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0014_auto_20151013_1353'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemfilelocation',
            name='file_object',
        ),
        migrations.RemoveField(
            model_name='itemfilelocation',
            name='item',
        ),
        migrations.DeleteModel(
            name='ItemFileLocation',
        ),
    ]
