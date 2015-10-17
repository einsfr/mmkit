# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
from django.conf import settings
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('common', '0015_auto_20151017_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, editable=False)),
                ('participants', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None, verbose_name='участники разговора', db_index=True)),
                ('conv_type', models.IntegerField(choices=[(0, 'диалог')], editable=False, verbose_name='тип разговора')),
            ],
            options={
                'verbose_name_plural': 'разговоры',
                'verbose_name': 'разговор',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False, editable=False)),
                ('content', models.TextField(verbose_name='содержание')),
                ('sended', models.DateTimeField(auto_now_add=True, verbose_name='время отправления')),
                ('readed', models.DateTimeField(editable=False, null=True, verbose_name='время прочтения')),
                ('important', models.BooleanField(default=False, verbose_name='важное')),
                ('msg_class', models.CharField(editable=False, blank=True, verbose_name='класс сообщения', max_length=64)),
                ('conversation', models.ForeignKey(editable=False, to='common.Conversation', verbose_name='разговор', related_name='messages')),
                ('receiver', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, verbose_name='получатель', related_name='+')),
                ('sender', models.ForeignKey(editable=False, null=True, to=settings.AUTH_USER_MODEL, verbose_name='отправитель', related_name='+')),
            ],
            options={
                'verbose_name_plural': 'сообщения',
                'verbose_name': 'сообщение',
            },
        ),
        migrations.AddField(
            model_name='conversation',
            name='last_message',
            field=models.OneToOneField(editable=False, to='common.Message', verbose_name='последнее сообщение', related_name='+'),
        ),
    ]
