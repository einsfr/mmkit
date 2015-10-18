# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0020_auto_20151018_0011'),
    ]

    operations = [
        migrations.CreateModel(
            name='IMUpdateChannel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('last_update', models.DateTimeField(verbose_name='последнее обновление', editable=False)),
                ('user', models.ForeignKey(editable=False, verbose_name='пользователь', related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': [],
            },
        ),
    ]
