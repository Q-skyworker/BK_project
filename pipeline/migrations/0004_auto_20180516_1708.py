# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pipeline', '0003_auto_20180206_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templatescheme',
            name='unique_id',
            field=models.CharField(unique=True, max_length=97, verbose_name='\u65b9\u6848\u552f\u4e00ID', blank=True),
        ),
    ]
