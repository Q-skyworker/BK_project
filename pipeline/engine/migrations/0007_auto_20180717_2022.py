# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0006_auto_20180717_1543'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scheduleservice',
            name='celery_id',
        ),
        migrations.RemoveField(
            model_name='scheduleservice',
            name='celery_info_lock',
        ),
        migrations.RemoveField(
            model_name='scheduleservice',
            name='is_frozen',
        ),
        migrations.RemoveField(
            model_name='scheduleservice',
            name='schedule_date',
        ),
    ]
