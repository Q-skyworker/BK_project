# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasktmpl3', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tasktemplate',
            options={'ordering': ['-id'], 'verbose_name': '\u6d41\u7a0b\u6a21\u677f TaskTemplate', 'verbose_name_plural': '\u6d41\u7a0b\u6a21\u677f TaskTemplate', 'permissions': [('common_select_steps', '\u6b65\u9aa4\u9009\u62e9'), ('common_fill_params', '\u53c2\u6570\u586b\u5199'), ('common_execute_task', '\u4efb\u52a1\u6267\u884c'), ('common_finished', '\u5b8c\u6210'), ('common_func_select_steps', '\u6b65\u9aa4\u9009\u62e9'), ('common_func_func_submit', '\u63d0\u4ea4\u9700\u6c42'), ('common_func_func_claim', '\u804c\u80fd\u5316\u8ba4\u9886'), ('common_func_execute_task', '\u4efb\u52a1\u6267\u884c'), ('common_func_finished', '\u5b8c\u6210')]},
        ),
    ]
