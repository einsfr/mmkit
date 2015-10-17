# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0018_auto_20151017_1610'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='conversation',
            options={'verbose_name_plural': 'разговоры', 'default_permissions': [], 'verbose_name': 'разговор'},
        ),
        migrations.AlterModelOptions(
            name='conversationlastmessage',
            options={'default_permissions': []},
        ),
        migrations.AlterModelOptions(
            name='message',
            options={'verbose_name_plural': 'сообщения', 'default_permissions': [], 'permissions': (('send_message', 'Can send messages'), ('receive_message', 'Can receive messages')), 'verbose_name': 'сообщение'},
        ),
    ]
