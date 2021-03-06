# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasktmpl3', '0002_auto_20180130_1633'),
        ('appmaker', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appmaker',
            name='task_flow',
        ),
        migrations.AddField(
            model_name='appmaker',
            name='edit_time',
            field=models.DateTimeField(auto_now=True, verbose_name='\u7f16\u8f91\u65f6\u95f4', null=True),
        ),
        migrations.AddField(
            model_name='appmaker',
            name='task_template',
            field=models.ForeignKey(default=None, verbose_name='\u5173\u8054\u6a21\u677f', to='tasktmpl3.TaskTemplate'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appmaker',
            name='template_schema_id',
            field=models.CharField(max_length=100, verbose_name='\u6267\u884c\u6267\u884c\u65b9\u6848', blank=True),
        ),
        migrations.AlterField(
            model_name='appmaker',
            name='default_viewer',
            field=models.TextField(default=b'{}', verbose_name='\u6dfb\u52a0\u5230\u684c\u9762'),
        ),
        migrations.AlterField(
            model_name='appmaker',
            name='desc',
            field=models.CharField(max_length=255, null=True, verbose_name='APP\u63cf\u8ff0\u4fe1\u606f'),
        ),
        migrations.AlterField(
            model_name='appmaker',
            name='editor',
            field=models.CharField(max_length=100, null=True, verbose_name='\u7f16\u8f91\u4eba'),
        ),
        migrations.AlterField(
            model_name='appmaker',
            name='info',
            field=models.CharField(max_length=255, null=True, verbose_name='APP\u57fa\u672c\u4fe1\u606f'),
        ),
    ]
