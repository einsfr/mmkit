# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0008_program_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(unique=True, verbose_name='название', max_length=64)),
                ('active', models.BooleanField(verbose_name='используется', default=True)),
            ],
            options={
                'verbose_name': 'канал',
                'verbose_name_plural': 'каналы',
            },
        ),
    ]
