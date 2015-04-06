# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lineup',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='название')),
                ('active_since', models.DateField(verbose_name='используется с')),
                ('active_until', models.DateField(verbose_name='используется до')),
                ('active', models.BooleanField(verbose_name='используется')),
            ],
            options={
                'verbose_name': 'сетка вещания',
                'verbose_name_plural': 'сетки вещания',
            },
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='название')),
                ('lineup_size', models.TimeField(verbose_name='размер в сетке вещания')),
                ('max_duration', models.TimeField(verbose_name='максимальный хронометраж')),
                ('min_duration', models.TimeField(verbose_name='минимальный хронометраж')),
                ('description', models.TextField(verbose_name='описание')),
                ('age_limit', models.SmallIntegerField(verbose_name='ограничение по возрасту', choices=[(0, '0+'), (16, '16+'), (18, '18+'), (12, '12+'), (6, '6+')])),
            ],
            options={
                'verbose_name': 'программа',
                'verbose_name_plural': 'программы',
            },
        ),
        migrations.CreateModel(
            name='ProgramPosition',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('dow', models.SmallIntegerField(verbose_name='день недели', choices=[(1, 'Понедельник'), (2, 'Вторник'), (3, 'Среда'), (4, 'Четверг'), (5, 'Пятница'), (6, 'Суббота'), (7, 'Воскресенье')])),
                ('start_time', models.TimeField(verbose_name='время начала')),
                ('comment', models.CharField(verbose_name='комментарий', max_length=32)),
            ],
            options={
                'verbose_name': 'положение программы в сетке вещания',
                'verbose_name_plural': 'положения программы в сетке вещания',
            },
        ),
    ]
