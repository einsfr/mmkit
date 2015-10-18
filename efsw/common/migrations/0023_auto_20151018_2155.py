# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0022_auto_20151018_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imupdatechannel',
            name='last_message_dt',
            field=models.DateTimeField(verbose_name='дата и время самого нового сообщения', editable=False),
        ),
    ]
