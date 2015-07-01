# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conversion', '0004_auto_20150701_1706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conversiontask',
            name='status',
            field=models.IntegerField(editable=False, choices=[(0, 'неизвестно'), (1, 'в очереди'), (2, 'ожидает запуска'), (3, 'запущено'), (4, 'выполняется'), (5, 'завершено'), (-1, 'ошибка')], default=1),
        ),
    ]
