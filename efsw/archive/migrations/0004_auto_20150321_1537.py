# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0003_itemlog_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('location', models.CharField(verbose_name='размещение', max_length=255)),
            ],
            options={
                'verbose_name': 'размещение моделей в хранилищах',
            },
        ),
        migrations.RemoveField(
            model_name='item',
            name='storage',
        ),
        migrations.AddField(
            model_name='storage',
            name='description',
            field=models.CharField(verbose_name='описание', max_length=255, default='Описание хранилища'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='storage',
            name='type',
            field=models.CharField(choices=[('ONS', 'Онлайн (без управления ФС)'), ('OFF', 'Оффлайн'), ('ONM', 'Онлайн (с управлением ФС)')], verbose_name='тип', max_length=3, default='ONM'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='itemlog',
            name='action',
            field=models.CharField(choices=[('ADD', 'Добавление'), ('IUP', 'Обновление связей'), ('UPD', 'Обновление')], max_length=3),
        ),
        migrations.AlterField(
            model_name='storage',
            name='base_url',
            field=models.CharField(verbose_name='базовая ссылка', blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='storage',
            name='mount_dir',
            field=models.CharField(verbose_name='точка монтирования', blank=True, max_length=32),
        ),
        migrations.AddField(
            model_name='itemlocation',
            name='item',
            field=models.ForeignKey(related_name='storages_locations', to='archive.Item'),
        ),
        migrations.AddField(
            model_name='itemlocation',
            name='storage',
            field=models.ForeignKey(related_name='items_locations', to='archive.Storage'),
        ),
        migrations.AddField(
            model_name='storage',
            name='items',
            field=models.ManyToManyField(related_name='stored_in', through='archive.ItemLocation', to='archive.Item'),
        ),
        migrations.AlterUniqueTogether(
            name='itemlocation',
            unique_together=set([('storage', 'item')]),
        ),
    ]
