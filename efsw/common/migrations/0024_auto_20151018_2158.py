# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0023_auto_20151018_2155'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imupdatechannel',
            old_name='last_message_dt',
            new_name='newest_message_dt',
        ),
    ]
