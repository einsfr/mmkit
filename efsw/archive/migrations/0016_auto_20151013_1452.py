# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0007_message'),
        ('archive', '0015_auto_20151013_1452'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemFileLocation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('file_object', models.ForeignKey(related_name='+', to='common.FileStorageObject')),
                ('item', models.ForeignKey(related_name='file_locations', to='archive.Item')),
            ],
            options={
                'default_permissions': ('change',),
            },
        ),
        migrations.AlterUniqueTogether(
            name='itemfilelocation',
            unique_together=set([('file_object', 'item')]),
        ),
    ]
