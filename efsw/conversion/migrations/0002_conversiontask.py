# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('conversion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConversionTask',
            fields=[
                ('order', models.PositiveIntegerField(verbose_name='порядок', db_index=True, editable=False)),
                ('id', models.UUIDField(editable=False, serialize=False, primary_key=True, default=uuid.uuid4)),
                ('args_builder', models.BinaryField()),
                ('status', models.IntegerField(editable=False, choices=[(0, 'неизвестно'), (1, 'в очереди'), (2, 'ожидает запуска'), (3, 'запущено'), (4, 'выполняется'), (5, 'завершено'), (-1, 'ошибка')])),
                ('added', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('processed_frames', models.PositiveIntegerField(null=True, editable=False)),
            ],
            options={
                'abstract': False,
                'ordering': ['order'],
            },
        ),
    ]
