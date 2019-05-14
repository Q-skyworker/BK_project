# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_business_time_zone'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='executor',
            field=models.CharField(max_length=100, verbose_name='\u4efb\u52a1\u6267\u884c\u8005', blank=True),
        ),
    ]
