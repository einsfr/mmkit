# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_message'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='postponed',
        ),
        migrations.AlterField(
            model_name='message',
            name='readed',
            field=models.DateTimeField(verbose_name='время прочтения', editable=False, null=True),
        ),
    ]
