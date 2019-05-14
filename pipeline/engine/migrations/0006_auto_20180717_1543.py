# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0005_auto_20180717_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduleservice',
            name='celery_id',
            field=models.CharField(max_length=36, null=True, verbose_name='celery \u4efb\u52a1ID'),
        ),
    ]
