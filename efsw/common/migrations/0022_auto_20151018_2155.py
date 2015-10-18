# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0021_imupdatechannel'),
    ]

    operations = [
        migrations.RenameField(
            model_name='imupdatechannel',
            old_name='last_update',
            new_name='last_message_dt',
        ),
    ]
