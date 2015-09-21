# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conversion', '0006_conversiontask_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='conversionprocess',
            options={'verbose_name_plural': 'процессы конвертирования', 'verbose_name': 'процесс конвертирования'},
        ),
        migrations.AlterModelOptions(
            name='conversionprofile',
            options={'ordering': ['-id'], 'verbose_name_plural': 'профили конвертирования', 'verbose_name': 'профиль конвертирования'},
        ),
        migrations.AlterModelOptions(
            name='conversiontask',
            options={'ordering': ['-added'], 'verbose_name_plural': 'задания конвертирования', 'verbose_name': 'задание конвертирования'},
        ),
        migrations.AlterField(
            model_name='conversiontask',
            name='status',
            field=models.IntegerField(default=1, choices=[(0, 'неизвестно'), (1, 'в очереди'), (2, 'ожидает запуска'), (3, 'запущено'), (4, 'выполняется'), (5, 'завершено'), (6, 'отменено'), (-1, 'ошибка')], editable=False),
        ),
    ]
