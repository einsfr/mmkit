# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0004_auto_20150321_1537'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='itemlocation',
            options={'verbose_name': 'размещение моделей в хранилищах', 'default_permissions': ('change',)},
        ),
        migrations.AlterField(
            model_name='itemlog',
            name='action',
            field=models.CharField(choices=[('UPD', 'Обновление'), ('ADD', 'Добавление'), ('IUP', 'Обновление связей')], max_length=3),
        ),
        migrations.AlterField(
            model_name='storage',
            name='type',
            field=models.CharField(choices=[('ONM', 'Онлайн (с управлением ФС)'), ('OFF', 'Оффлайн'), ('ONS', 'Онлайн (без управления ФС)')], verbose_name='тип', max_length=3),
        ),
    ]
