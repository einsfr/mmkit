# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import efsw.common.db.models


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0003_itemlog_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storage',
            name='base_url',
        ),
        migrations.RemoveField(
            model_name='storage',
            name='mount_dir',
        ),
        migrations.AddField(
            model_name='storage',
            name='extra_data',
            field=efsw.common.db.models.ExtraDataField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name='storage',
            name='type',
            field=models.CharField(verbose_name='тип', max_length=3, default='ONM', choices=[('ONM', 'Онлайн (с управлением ФС)'), ('OFF', 'Оффлайн'), ('ONS', 'Онлайн (без управления ФС)')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='itemlog',
            name='action',
            field=models.CharField(max_length=3, choices=[('IUP', 'Обновление связей'), ('ADD', 'Добавление'), ('UPD', 'Обновление')]),
        ),
    ]
