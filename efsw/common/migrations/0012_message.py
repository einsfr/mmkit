# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0011_auto_20151016_1011'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(serialize=False, editable=False, primary_key=True, default=uuid.uuid4)),
                ('content', models.TextField(verbose_name='содержание')),
                ('sended', models.DateTimeField(auto_now_add=True, verbose_name='время отправления')),
                ('readed', models.DateTimeField(editable=False, null=True, verbose_name='время прочтения')),
                ('important', models.BooleanField(default=False, verbose_name='важное')),
                ('msg_class', models.CharField(editable=False, blank=True, verbose_name='класс сообщения', max_length=64)),
                ('conversation', models.ForeignKey(editable=False, related_name='messages', to='common.Conversation', verbose_name='разговор')),
                ('receiver', models.ForeignKey(editable=False, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='получатель')),
                ('sender', models.ForeignKey(editable=False, related_name='+', to=settings.AUTH_USER_MODEL, null=True, verbose_name='отправитель')),
            ],
            options={
                'verbose_name_plural': 'сообщения',
                'verbose_name': 'сообщение',
            },
        ),
    ]
