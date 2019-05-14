# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ComponentModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(unique=True, max_length=255, verbose_name='\u7ec4\u4ef6\u7f16\u7801')),
                ('name', models.CharField(max_length=255, verbose_name='\u7ec4\u4ef6\u540d\u79f0')),
                ('status', models.BooleanField(default=True, verbose_name='\u7ec4\u4ef6\u662f\u5426\u53ef\u7528')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': '\u7ec4\u4ef6',
                'verbose_name_plural': '\u7ec4\u4ef6',
            },
        ),
    ]
