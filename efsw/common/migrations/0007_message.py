# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0006_auto_20150720_1923'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False)),
                ('content', models.TextField(verbose_name='содержание')),
                ('sended', models.DateTimeField(auto_now_add=True, verbose_name='время отправления')),
                ('readed', models.DateTimeField(verbose_name='время прочтения', editable=False)),
                ('important', models.BooleanField(default=False, verbose_name='важное')),
                ('postponed', models.BooleanField(default=False, verbose_name='отложено')),
                ('msg_class', models.CharField(blank=True, editable=False, max_length=64, verbose_name='класс сообщения')),
                ('receiver', models.ForeignKey(verbose_name='получатель', to=settings.AUTH_USER_MODEL, editable=False, related_name='+')),
                ('sender', models.ForeignKey(verbose_name='отправитель', to=settings.AUTH_USER_MODEL, editable=False, null=True, related_name='+')),
            ],
            options={
                'verbose_name': 'сообщение',
                'verbose_name_plural': 'сообщения',
            },
        ),
    ]
