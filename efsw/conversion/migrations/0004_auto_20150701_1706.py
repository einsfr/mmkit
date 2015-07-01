# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('conversion', '0003_conversiontask_error_msg'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConversionProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, verbose_name='название', max_length=255)),
                ('description', models.TextField(blank=True, verbose_name='описание')),
                ('args_builder', models.BinaryField()),
            ],
        ),
        migrations.AddField(
            model_name='conversiontask',
            name='io_conf',
            field=models.BinaryField(default=b'\x80\x03N.'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='conversiontask',
            name='args_builder',
            field=models.BinaryField(null=True),
        ),
        migrations.AddField(
            model_name='conversiontask',
            name='conv_profile',
            field=models.ForeignKey(to='conversion.ConversionProfile', null=True, related_name='+', editable=False),
        ),
    ]
