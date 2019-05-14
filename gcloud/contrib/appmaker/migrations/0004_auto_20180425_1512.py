# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmaker', '0003_auto_20180301_1729'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appmaker',
            name='default_viewer',
        ),
        migrations.AlterField(
            model_name='appmaker',
            name='template_schema_id',
            field=models.CharField(max_length=100, verbose_name='\u6267\u884c\u65b9\u6848', blank=True),
        ),
    ]
