# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.UUIDField(serialize=False, default=uuid.uuid4, primary_key=True, editable=False)),
                ('participants', django.contrib.postgres.fields.ArrayField(db_index=True, size=None, verbose_name='участники разговора', base_field=models.IntegerField())),
                ('conv_type', models.IntegerField(verbose_name='тип разговора', choices=[(0, 'диалог')], editable=False)),
            ],
            options={
                'verbose_name_plural': 'разговоры',
                'verbose_name': 'разговор',
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='IMUpdateChannel',
            fields=[
                ('id', models.UUIDField(serialize=False, default=uuid.uuid4, primary_key=True, editable=False)),
                ('newest_message_dt', models.DateTimeField(verbose_name='дата и время отправления самого нового сообщения', editable=False)),
                ('last_time_used', models.DateTimeField(verbose_name='дата и время последнего обращения к каналу', editable=False)),
                ('user', models.ForeignKey(editable=False, verbose_name='пользователь', to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(serialize=False, default=uuid.uuid4, primary_key=True, editable=False)),
                ('content', models.TextField(verbose_name='содержание')),
                ('sent', models.DateTimeField(verbose_name='время отправления', auto_now_add=True)),
                ('read', models.DateTimeField(null=True, verbose_name='время прочтения', editable=False)),
                ('important', models.BooleanField(verbose_name='важное', default=False)),
                ('msg_class', models.CharField(blank=True, max_length=64, verbose_name='класс сообщения', editable=False)),
            ],
            options={
                'permissions': (('send_message', 'Can send messages'), ('receive_message', 'Can receive messages')),
                'verbose_name': 'сообщение',
                'default_permissions': [],
                'verbose_name_plural': 'сообщения',
            },
        ),
        migrations.CreateModel(
            name='ConversationLastMessage',
            fields=[
                ('conversation', models.OneToOneField(primary_key=True, serialize=False, editable=False, to='im.Conversation', related_name='last_message')),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.AddField(
            model_name='message',
            name='conversation',
            field=models.ForeignKey(editable=False, verbose_name='разговор', to='im.Conversation', related_name='messages'),
        ),
        migrations.AddField(
            model_name='message',
            name='receiver',
            field=models.ForeignKey(editable=False, verbose_name='получатель', to=settings.AUTH_USER_MODEL, related_name='+'),
        ),
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(null=True, editable=False, verbose_name='отправитель', to=settings.AUTH_USER_MODEL, related_name='+'),
        ),
        migrations.AddField(
            model_name='conversationlastmessage',
            name='message',
            field=models.OneToOneField(editable=False, to='im.Message', related_name='+'),
        ),
    ]
