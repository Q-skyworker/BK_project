# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0004_auto_20180717_1411'),
    ]

    operations = [
        migrations.AlterField(
            model_name='functionswitch',
            name='name',
            field=models.CharField(unique=True, max_length=32, verbose_name='\u529f\u80fd\u540d\u79f0'),
        ),
    ]
