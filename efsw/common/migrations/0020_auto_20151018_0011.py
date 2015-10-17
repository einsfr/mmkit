# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0019_auto_20151017_2345'),
    ]

    operations = [
        migrations.RenameField(
            model_name='message',
            old_name='readed',
            new_name='read',
        ),
        migrations.RenameField(
            model_name='message',
            old_name='sended',
            new_name='sent',
        ),
    ]
