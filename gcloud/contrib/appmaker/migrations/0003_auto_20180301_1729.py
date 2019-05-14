# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appmaker', '0002_auto_20180209_1510'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='appmaker',
            options={'ordering': ['-id'], 'verbose_name': '\u8f7b\u5e94\u7528 AppMaker', 'verbose_name_plural': '\u8f7b\u5e94\u7528 AppMaker'},
        ),
    ]
