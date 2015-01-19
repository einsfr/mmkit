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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemFolder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('item', models.ForeignKey(related_name='folders', to='archive.Item')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ItemLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dt', models.DateTimeField(auto_now=True)),
                ('action', models.CharField(max_length=3, choices=[('UPD', 'Обновление'), ('ADD', 'Добавление')])),
                ('item', models.ForeignKey(related_name='log', to='archive.Item')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('base_url', models.CharField(max_length=255, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='itemfile',
            name='folder',
            field=models.ForeignKey(related_name='files', to='archive.ItemFolder'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='category',
            field=models.ForeignKey(related_name='items', to='archive.ItemCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='includes',
            field=models.ManyToManyField(related_name='included_in', to='archive.Item'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='item',
            name='storage',
            field=models.ForeignKey(related_name='items', to='archive.Storage'),
            preserve_default=True,
        ),
    ]
