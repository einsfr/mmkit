# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import efsw.common.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0004_auto_20150317_2249'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseOnlineStorage',
            fields=[
            ],
            options={
                'verbose_name': 'хранилище',
                'proxy': True,
                'verbose_name_plural': 'хранилищи',
            },
            bases=('archive.storage',),
        ),
        migrations.CreateModel(
            name='OfflineStorage',
            fields=[
            ],
            options={
                'verbose_name': 'хранилище',
                'proxy': True,
                'verbose_name_plural': 'хранилищи',
            },
            bases=('archive.storage',),
        ),
        migrations.AlterModelOptions(
            name='storage',
            options={},
        ),
        migrations.AddField(
            model_name='item',
            name='extra_data',
            field=efsw.common.db.models.ExtraDataField(blank=True, null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='itemlog',
            name='action',
            field=models.CharField(choices=[('UPD', 'Обновление'), ('ADD', 'Добавление'), ('IUP', 'Обновление связей')], max_length=3),
        ),
        migrations.AlterField(
            model_name='storage',
            name='type',
            field=models.CharField(choices=[('OFF', 'Оффлайн'), ('ONM', 'Онлайн (с управлением ФС)'), ('ONS', 'Онлайн (без управления ФС)')], verbose_name='тип', max_length=3),
        ),
        migrations.CreateModel(
            name='OnlineMasterStorage',
            fields=[
            ],
            options={
                'verbose_name': 'хранилище',
                'proxy': True,
                'verbose_name_plural': 'хранилищи',
            },
            bases=('archive.baseonlinestorage',),
        ),
        migrations.CreateModel(
            name='OnlineSlaveStorage',
            fields=[
            ],
            options={
                'verbose_name': 'хранилище',
                'proxy': True,
                'verbose_name_plural': 'хранилищи',
            },
            bases=('archive.baseonlinestorage',),
        ),
    ]
