# -*- coding: utf-8 -*-
import os

from pipeline.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'Generate Redis & Supervisor configuration file for pipeline'

    configs = {
        os.path.join(settings.BASE_DIR, 'etc/redis.conf'): 'redis/redis.tmpl',
        os.path.join(settings.BASE_DIR, 'etc/supervisord.conf'): 'supervisor/supervisor.tmpl'
    }

    var_paths = [
        os.path.join(settings.BASE_DIR, 'var/log/'),
        os.path.join(settings.BASE_DIR, 'var/run/')
    ]

    def add_arguments(self, parser):
        parser.add_argument('-pc',
                            dest='p_worker_num',
                            default=2,
                            help='Set number of worker bind with pipeline')
        parser.add_argument('-sc',
                            dest='s_worker_num',
                            default=2,
                            help='Set the number of worker bind with schedule')
        parser.add_argument('--worker',
                            action='store_true',
                            dest='is_worker',
                            default=False,
                            help='is worker process group (default False)')
        parser.add_argument('--master',
                            action='store_true',
                            dest='is_master',
                            default=False,
                            help='is master process group (default False)')

    def handle(self, *args, **options):
        context = {
            'settings': settings,
            'is_master': options['is_master'],
            'is_worker': options['is_worker'],
            'p_worker_num': options['p_worker_num'],
            's_worker_num': options['s_worker_num'],
            'uid': os.getuid()
        }

        for path in self.var_paths:
            if not os.path.exists(path):
                os.makedirs(path)

        for target_path, template_name in self.configs.iteritems():
            dirname = os.path.dirname(target_path)
            if not os.path.exists(dirname):
                try:
                    os.makedirs(dirname)
                except:
                    pass

            with open(target_path, 'wb+') as f:
                f.write(
                    render_to_string(template_name, context)
                )
