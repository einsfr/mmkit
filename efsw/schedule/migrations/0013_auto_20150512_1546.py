# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0012_auto_20150503_2112'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='channel',
            options={'ordering': ['name'], 'verbose_name': 'канал', 'verbose_name_plural': 'каналы'},
        ),
        migrations.RemoveField(
            model_name='lineup',
            name='active',
        ),
        migrations.AddField(
            model_name='lineup',
            name='draft',
            field=models.BooleanField(verbose_name='черновик', default=True),
        ),
    ]
