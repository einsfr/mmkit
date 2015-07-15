# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0011_auto_20150709_1721'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='itemfilelocation',
            options={'default_permissions': ('change',)},
        ),
    ]
