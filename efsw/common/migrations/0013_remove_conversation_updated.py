# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0012_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='conversation',
            name='updated',
        ),
    ]
