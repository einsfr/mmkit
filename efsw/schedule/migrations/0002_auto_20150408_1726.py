# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='programposition',
            name='lineup',
            field=models.ForeignKey(related_name='program_positions', default=0, to='schedule.Lineup'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='programposition',
            name='program',
            field=models.ForeignKey(related_name='lineup_positions', default=0, to='schedule.Program'),
            preserve_default=False,
        ),
    ]
