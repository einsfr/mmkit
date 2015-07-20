# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0005_auto_20150717_1003'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='filestorageobject',
            unique_together=set([]),
        ),
    ]
