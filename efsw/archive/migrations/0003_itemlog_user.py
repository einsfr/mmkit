# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('archive', '0002_auto_20150303_0950'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemlog',
            name='user',
            field=models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
