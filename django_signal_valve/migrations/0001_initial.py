# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_signal_valve.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Signal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module_path', models.TextField(verbose_name='\u4fe1\u53f7\u6a21\u5757\u540d')),
                ('name', models.CharField(max_length=64, verbose_name='\u4fe1\u53f7\u5c5e\u6027\u540d')),
                ('kwargs', django_signal_valve.models.IOField(verbose_name='\u4fe1\u53f7\u53c2\u6570')),
            ],
        ),
    ]
