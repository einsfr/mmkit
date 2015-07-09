# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0009_auto_20150709_0959'),
    ]

    operations = [
        migrations.RenameField(
            model_name='itemfilelocation',
            old_name='id',
            new_name='file_object',
        ),
        migrations.RenameField(
            model_name='itemmetalocation',
            old_name='item_id',
            new_name='item',
        ),
        migrations.RenameField(
            model_name='itemmetalocation',
            old_name='id',
            new_name='meta_object',
        ),
        migrations.AlterField(
            model_name='itemlog',
            name='action',
            field=models.CharField(max_length=3, choices=[('ADD', 'Добавление'), ('UPD', 'Обновление'), ('IUP', 'Обновление связей')]),
        ),
        migrations.AlterField(
            model_name='storage',
            name='type',
            field=models.CharField(max_length=3, verbose_name='тип', choices=[('ONS', 'Онлайн (без управления ФС)'), ('ONM', 'Онлайн (с управлением ФС)'), ('OFF', 'Оффлайн')]),
        ),
    ]
