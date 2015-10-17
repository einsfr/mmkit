# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0017_auto_20151017_1425'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ConversationLastMessageCache',
            new_name='ConversationLastMessage',
        ),
    ]
