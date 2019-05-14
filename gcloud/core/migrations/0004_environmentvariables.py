# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_business_executor'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnvironmentVariables',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=255, verbose_name='\u53d8\u91cfKEY')),
                ('name', models.CharField(max_length=255, verbose_name='\u53d8\u91cf\u63cf\u8ff0', blank=True)),
                ('value', models.CharField(max_length=1000, verbose_name='\u53d8\u91cf\u503c', blank=True)),
            ],
            options={
                'verbose_name': '\u73af\u5883\u53d8\u91cf EnvironmentVariables',
                'verbose_name_plural': '\u73af\u5883\u53d8\u91cf EnvironmentVariables',
            },
        ),
    ]
