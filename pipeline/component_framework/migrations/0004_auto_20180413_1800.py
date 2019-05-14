# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('component_framework', '0003_componentmodel'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='componentmodel',
            options={'ordering': ['-id'], 'verbose_name': '\u7ec4\u4ef6 Component', 'verbose_name_plural': '\u7ec4\u4ef6 Component'},
        ),
    ]
