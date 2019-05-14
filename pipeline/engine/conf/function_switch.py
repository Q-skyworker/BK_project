# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _

FREEZE_ENGINE = 'FREEZE_ENGINE'

switch_list = [
    {
        'name': FREEZE_ENGINE,
        'description': _(u"用于冻结引擎, 冻结期间会屏蔽所有内部信号及暂停所有进程，同时拒绝所有 web 流程控制请求"),
        'is_active': False
    }
]
