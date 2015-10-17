# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0016_auto_20151017_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConversationLastMessageCache',
            fields=[
                ('conversation', models.OneToOneField(editable=False, to='common.Conversation', related_name='last_message', serialize=False, primary_key=True)),
                ('message', models.OneToOneField(to='common.Message', related_name='+', editable=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='conversation',
            name='last_message',
        ),
    ]
