# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0010_auto_20150709_1001'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='itemlocation',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='itemlocation',
            name='item',
        ),
        migrations.RemoveField(
            model_name='itemlocation',
            name='storage',
        ),
        migrations.RemoveField(
            model_name='itemmetalocation',
            name='item',
        ),
        migrations.RemoveField(
            model_name='itemmetalocation',
            name='meta_object',
        ),
        migrations.RemoveField(
            model_name='storage',
            name='items',
        ),
        migrations.DeleteModel(
            name='ItemLocation',
        ),
        migrations.DeleteModel(
            name='ItemMetaLocation',
        ),
        migrations.DeleteModel(
            name='Storage',
        ),
    ]
