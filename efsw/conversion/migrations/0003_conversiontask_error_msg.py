# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conversion', '0002_conversiontask'),
    ]

    operations = [
        migrations.AddField(
            model_name='conversiontask',
            name='error_msg',
            field=models.CharField(editable=False, blank=True, max_length=1024),
        ),
    ]
