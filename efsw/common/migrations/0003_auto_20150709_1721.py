# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0011_auto_20150709_1721'),
        ('common', '0002_auto_20150709_1341'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='metastorageobject',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='metastorageobject',
            name='storage',
        ),
        migrations.DeleteModel(
            name='MetaStorage',
        ),
        migrations.DeleteModel(
            name='MetaStorageObject',
        ),
    ]
