# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0007_auto_20180717_2022'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScheduleCeleryTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('schedule_id', models.CharField(unique=True, max_length=64, verbose_name='schedule ID', db_index=True)),
                ('celery_task_id', models.CharField(default=b'', max_length=40, verbose_name='celery \u4efb\u52a1 ID')),
            ],
        ),
    ]
