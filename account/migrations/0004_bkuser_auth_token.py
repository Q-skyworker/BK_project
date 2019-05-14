# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20161031_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='bkuser',
            name='auth_token',
            field=models.CharField(default=b'', max_length=255, verbose_name='auth_token', blank=True),
        ),
    ]
