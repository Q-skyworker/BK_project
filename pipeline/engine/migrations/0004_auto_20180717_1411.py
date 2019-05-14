# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0003_auto_20180717_1148'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pipelineprocess',
            old_name='is_froze',
            new_name='is_frozen',
        ),
    ]
