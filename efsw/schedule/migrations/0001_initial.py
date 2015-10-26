# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import efsw.common.db.models.fields.color
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64, verbose_name='название')),
                ('active', models.BooleanField(verbose_name='используется', default=True)),
            ],
            options={
                'verbose_name': 'канал',
                'verbose_name_plural': 'каналы',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='DayLineup',
            fields=[
                ('start_time', models.TimeField(verbose_name='время начала эфирных суток')),
                ('end_time', models.TimeField(verbose_name='время окончания эфирных суток')),
                ('id', models.UUIDField(serialize=False, default=uuid.uuid4, primary_key=True, editable=False)),
                ('day', models.DateField(verbose_name='дата')),
                ('channel', models.ForeignKey(to='schedule.Channel', verbose_name='канал', related_name='+')),
            ],
            options={
                'verbose_name': 'программа на день',
                'verbose_name_plural': 'программы на день',
            },
        ),
        migrations.CreateModel(
            name='DayLineupItem',
            fields=[
                ('order', models.PositiveIntegerField(db_index=True, verbose_name='порядок', editable=False)),
                ('id', models.UUIDField(serialize=False, default=uuid.uuid4, primary_key=True, editable=False)),
                ('day_lineup', models.ForeignKey(to='schedule.DayLineup', verbose_name='программа на день', related_name='items')),
            ],
            options={
                'verbose_name': 'элемент программы на день',
                'verbose_name_plural': 'элементы программы на день',
            },
        ),
        migrations.CreateModel(
            name='DayLineupTemplate',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('start_time', models.TimeField(verbose_name='время начала эфирных суток')),
                ('end_time', models.TimeField(verbose_name='время окончания эфирных суток')),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='имя шаблона')),
                ('channel', models.ForeignKey(to='schedule.Channel', verbose_name='канал', related_name='+')),
            ],
            options={
                'verbose_name': 'шаблон программы на день',
                'verbose_name_plural': 'шаблоны программ на день',
            },
        ),
        migrations.CreateModel(
            name='DayLineupTemplateItem',
            fields=[
                ('order', models.PositiveIntegerField(db_index=True, verbose_name='порядок', editable=False)),
                ('id', models.UUIDField(serialize=False, default=uuid.uuid4, primary_key=True, editable=False)),
                ('day_lineup_template', models.ForeignKey(to='schedule.DayLineupTemplate', verbose_name='шаблон программы на день', related_name='items')),
            ],
            options={
                'verbose_name': 'элемент шаблона программы на день',
                'verbose_name_plural': 'элементы шаблона программы на день',
            },
        ),
        migrations.CreateModel(
            name='Lineup',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='название')),
                ('active_since', models.DateField(null=True, verbose_name='используется с')),
                ('active_until', models.DateField(null=True, verbose_name='используется до')),
                ('draft', models.BooleanField(verbose_name='черновик', default=True)),
                ('start_time', models.TimeField(verbose_name='время начала эфирных суток')),
                ('end_time', models.TimeField(verbose_name='время окончания эфирных суток')),
                ('channel', models.ForeignKey(to='schedule.Channel', verbose_name='канал', related_name='lineups')),
            ],
            options={
                'verbose_name': 'сетка вещания',
                'verbose_name_plural': 'сетки вещания',
            },
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='название')),
                ('lineup_size', models.TimeField(verbose_name='размер в сетке вещания')),
                ('max_duration', models.TimeField(verbose_name='максимальный хронометраж')),
                ('min_duration', models.TimeField(verbose_name='минимальный хронометраж')),
                ('description', models.TextField(verbose_name='описание')),
                ('age_limit', models.SmallIntegerField(verbose_name='ограничение по возрасту', default=0, choices=[(0, '0+'), (16, '16+'), (18, '18+'), (12, '12+'), (6, '6+')])),
                ('color', efsw.common.db.models.fields.color.ColorField(max_length=7, verbose_name='цвет фона', default='#ffffff')),
            ],
            options={
                'verbose_name': 'программа',
                'verbose_name_plural': 'программы',
            },
        ),
        migrations.CreateModel(
            name='ProgramPosition',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('dow', models.SmallIntegerField(verbose_name='день недели', choices=[(1, 'Понедельник'), (2, 'Вторник'), (3, 'Среда'), (4, 'Четверг'), (5, 'Пятница'), (6, 'Суббота'), (7, 'Воскресенье')])),
                ('start_time', models.TimeField(verbose_name='время начала')),
                ('end_time', models.TimeField(verbose_name='время окончания')),
                ('comment', models.CharField(blank=True, max_length=32, verbose_name='комментарий')),
                ('locked', models.BooleanField(verbose_name='заблокировано', default=False)),
                ('lineup', models.ForeignKey(to='schedule.Lineup', related_name='program_positions')),
                ('program', models.ForeignKey(null=True, to='schedule.Program', blank=True, related_name='lineup_positions')),
            ],
            options={
                'verbose_name': 'положение программы в сетке вещания',
                'verbose_name_plural': 'положения программы в сетке вещания',
            },
        ),
    ]
