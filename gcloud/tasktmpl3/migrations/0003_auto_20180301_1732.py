# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasktmpl3', '0002_auto_20180130_1633'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tasktemplate',
            options={'ordering': ['-id'], 'verbose_name': '\u6d41\u7a0b\u6a21\u677f TaskTemplate', 'verbose_name_plural': '\u6d41\u7a0b\u6a21\u677f TaskTemplate', 'permissions': [('fill_params', '\u53c2\u6570\u586b\u5199'), ('execute_task', '\u4efb\u52a1\u6267\u884c')]},
        ),
    ]
