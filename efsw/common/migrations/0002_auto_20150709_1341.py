# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='filestorageobject',
            unique_together=set([('storage', 'id')]),
        ),
        migrations.AlterUniqueTogether(
            name='metastorageobject',
            unique_together=set([('storage', 'id')]),
        ),
    ]
