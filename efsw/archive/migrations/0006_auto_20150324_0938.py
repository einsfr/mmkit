# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0005_auto_20150322_2138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemlocation',
            name='item',
            field=models.ForeignKey(to='archive.Item', related_name='locations'),
        ),
        migrations.AlterField(
            model_name='itemlocation',
            name='storage',
            field=models.ForeignKey(to='archive.Storage', related_name='locations'),
        ),
        migrations.AlterField(
            model_name='itemlog',
            name='action',
            field=models.CharField(choices=[('IUP', 'Обновление связей'), ('ADD', 'Добавление'), ('UPD', 'Обновление')], max_length=3),
        ),
    ]
