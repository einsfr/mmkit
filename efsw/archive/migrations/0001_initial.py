# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import efsw.search.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('storage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='название')),
                ('description', models.TextField(verbose_name='описание')),
                ('created', models.DateField(verbose_name='дата создания')),
                ('author', models.CharField(max_length=255, verbose_name='автор')),
            ],
            options={
                'verbose_name': 'элемент',
                'verbose_name_plural': 'элементы',
            },
            bases=(efsw.search.models.IndexableModel, models.Model),
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64, verbose_name='название')),
            ],
            options={
                'verbose_name': 'категория',
                'verbose_name_plural': 'категории',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ItemFileLocation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('file_object', models.ForeignKey(to='storage.FileStorageObject', related_name='+')),
                ('item', models.ForeignKey(to='archive.Item', related_name='file_locations')),
            ],
            options={
                'default_permissions': ('change',),
            },
        ),
        migrations.CreateModel(
            name='ItemLog',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('dt', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(max_length=3, choices=[('IUP', 'Обновление связей'), ('UPD', 'Обновление'), ('ADD', 'Добавление')])),
                ('item', models.ForeignKey(to='archive.Item', related_name='log')),
                ('user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
            options={
                'verbose_name_plural': 'записи',
                'verbose_name': 'запись',
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(to='archive.ItemCategory', verbose_name='категория', related_name='items'),
        ),
        migrations.AddField(
            model_name='item',
            name='includes',
            field=models.ManyToManyField(related_name='included_in', to='archive.Item'),
        ),
        migrations.AlterUniqueTogether(
            name='itemfilelocation',
            unique_together=set([('file_object', 'item')]),
        ),
    ]
