# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConversionProcess',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('conv_id', models.UUIDField(unique=True, editable=False)),
                ('pid', models.PositiveIntegerField(editable=False)),
            ],
            options={
                'verbose_name': 'процесс конвертирования',
                'verbose_name_plural': 'процессы конвертирования',
            },
        ),
        migrations.CreateModel(
            name='ConversionProfile',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='название')),
                ('description', models.TextField(blank=True, verbose_name='описание')),
                ('args_builder', models.BinaryField()),
            ],
            options={
                'verbose_name': 'профиль конвертирования',
                'verbose_name_plural': 'профили конвертирования',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='ConversionTask',
            fields=[
                ('order', models.PositiveIntegerField(db_index=True, verbose_name='порядок', editable=False)),
                ('id', models.UUIDField(serialize=False, default=uuid.uuid4, primary_key=True, editable=False)),
                ('name', models.CharField(max_length=255)),
                ('args_builder', models.BinaryField(null=True)),
                ('io_conf', models.BinaryField()),
                ('status', models.IntegerField(choices=[(0, 'неизвестно'), (1, 'в очереди'), (2, 'ожидает запуска'), (3, 'запущено'), (4, 'выполняется'), (5, 'завершено'), (6, 'отменено'), (-1, 'ошибка')], default=1, editable=False)),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('processed_frames', models.PositiveIntegerField(null=True, editable=False)),
                ('error_msg', models.CharField(blank=True, max_length=1024, editable=False)),
                ('conv_profile', models.ForeignKey(null=True, editable=False, to='conversion.ConversionProfile', related_name='+')),
            ],
            options={
                'verbose_name': 'задание конвертирования',
                'verbose_name_plural': 'задания конвертирования',
                'ordering': ['-added'],
            },
        ),
    ]
