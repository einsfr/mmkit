# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='itemfile',
            name='folder',
        ),
        migrations.DeleteModel(
            name='ItemFile',
        ),
        migrations.RemoveField(
            model_name='itemfolder',
            name='item',
        ),
        migrations.DeleteModel(
            name='ItemFolder',
        ),
        migrations.AlterModelOptions(
            name='item',
            options={'verbose_name': 'элемент', 'verbose_name_plural': 'элементы'},
        ),
        migrations.AlterModelOptions(
            name='itemcategory',
            options={'verbose_name': 'категория', 'verbose_name_plural': 'категории'},
        ),
        migrations.AlterModelOptions(
            name='itemlog',
            options={'verbose_name': 'запись', 'verbose_name_plural': 'записи', 'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='storage',
            options={'verbose_name': 'хранилище', 'verbose_name_plural': 'хранилищи'},
        ),
        migrations.AlterField(
            model_name='item',
            name='author',
            field=models.CharField(verbose_name='автор', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.ForeignKey(related_name='items', verbose_name='категория', to='archive.ItemCategory'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='created',
            field=models.DateField(verbose_name='дата создания'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='description',
            field=models.TextField(verbose_name='описание'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(verbose_name='название', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='item',
            name='storage',
            field=models.ForeignKey(related_name='items', verbose_name='хранилище', to='archive.Storage'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='itemcategory',
            name='name',
            field=models.CharField(verbose_name='название', unique=True, max_length=64),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='itemlog',
            name='action',
            field=models.CharField(choices=[('UPD', 'Обновление'), ('IUP', 'Обновление связей'), ('ADD', 'Добавление')], max_length=3),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='storage',
            name='base_url',
            field=models.CharField(verbose_name='базовая ссылка', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='storage',
            name='mount_dir',
            field=models.CharField(verbose_name='точка монтирования', max_length=32),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='storage',
            name='name',
            field=models.CharField(verbose_name='имя', max_length=255),
            preserve_default=True,
        ),
    ]
