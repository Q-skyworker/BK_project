# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('function', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='functiontask',
            options={'ordering': ['-id'], 'verbose_name': '\u804c\u80fd\u5316\u8ba4\u9886\u5355 FunctionTask', 'verbose_name_plural': '\u804c\u80fd\u5316\u8ba4\u9886\u5355 FunctionTask'},
        ),
    ]
