# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('created', models.DateField()),
                ('author', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=64)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemFolder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=32)),
                ('item', models.ForeignKey(to='archive.Item', related_name='folders')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('dt', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(choices=[('ADD', 'Добавление'), ('UPD', 'Обновление')], max_length=3)),
                ('item', models.ForeignKey(to='archive.Item', related_name='log')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=255)),
                ('base_url', models.CharField(max_length=255)),
                ('mount_dir', models.CharField(max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='itemfile',
            name='folder',
            field=models.ForeignKey(to='archive.ItemFolder', related_name='files'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(to='archive.ItemCategory', related_name='items'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='includes',
            field=models.ManyToManyField(to='archive.Item', related_name='included_in'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='storage',
            field=models.ForeignKey(to='archive.Storage', related_name='items'),
            preserve_default=True,
        ),
    ]
