# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0006_auto_20150324_0938'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='itemcategory',
            options={'verbose_name_plural': 'категории', 'verbose_name': 'категория', 'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='storage',
            options={'verbose_name_plural': 'хранилищи', 'verbose_name': 'хранилище', 'ordering': ['name']},
        ),
    ]
