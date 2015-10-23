# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
import efsw.common.db.models.fields.color


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0013_auto_20150512_1546'),
    ]

    operations = [
        migrations.CreateModel(
            name='DayLineup',
            fields=[
                ('id', models.UUIDField(serialize=False, primary_key=True, editable=False, default=uuid.uuid4)),
                ('day', models.DateField(verbose_name='дата')),
                ('start_time', models.TimeField(verbose_name='время начала эфирных суток')),
                ('end_time', models.TimeField(verbose_name='время окончания эфирных суток')),
                ('channel', models.ForeignKey(to='schedule.Channel', related_name='+', verbose_name='канал')),
            ],
            options={
                'verbose_name': 'программа на день',
                'verbose_name_plural': 'программы на день',
            },
        ),
        migrations.CreateModel(
            name='DayLineupTemplate',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(verbose_name='имя шаблона', max_length=255, unique=True)),
                ('start_time', models.TimeField(verbose_name='время начала эфирных суток')),
                ('end_time', models.TimeField(verbose_name='время окончания эфирных суток')),
                ('channel', models.ForeignKey(to='schedule.Channel', related_name='+', verbose_name='канал')),
            ],
            options={
                'verbose_name': 'шаблон программы на день',
                'verbose_name_plural': 'шаблоны программ на день',
            },
        ),
    ]
