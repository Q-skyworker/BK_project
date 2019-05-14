# -*- coding: utf-8 -*-
import datetime
import re

from django.utils.translation import ugettext_lazy as _

from pipeline.conf import settings
from pipeline.core.flow.activity import Service, StaticIntervalGenerator
from pipeline.component_framework.component import Component

__group_name__ = _(u"蓝鲸服务(BK)")


class PauseService(Service):
    __need_schedule__ = True

    def execute(self, data, parent_data):
        return True

    def schedule(self, data, parent_data, callback_data=None):
        return True

    def outputs_format(self):
        return []


class PauseComponent(Component):
    name = _(u'暂停')
    code = 'pause_node'
    bound_service = PauseService
    form = settings.STATIC_URL + 'components/atoms/bk/pause.js'


class SleepTimerService(Service):
    __need_schedule__ = True
    interval = StaticIntervalGenerator(2)

    def execute(self, data, parent_data):
        timing = str(data.get_one_of_inputs('bk_timing'))
        #  匹配年月日 时分秒 正则 yyyy-MM-dd HH:mm:ss
        date_regex = r'^(((\d{3}[1-9]|\d{2}[1-9]\d{1}|\d{1}[1-9]\d{2}|[1-9]\d{3}))|' \
                     '(29/02/((\d{2})(0[48]|[2468][048]|[13579][26])|((0[48]|[2468][048]|[3579][26])00))))-' \
                     '((0[13578]|1[02])-((0[1-9]|[12]\d|3[01]))|' \
                     '((0[469]|11)-(0[1-9]|[12]\d|30))|(02)-(0[1-9]|[1]\d|2[0-8]))'
        #  时间正则
        time_regax = r'((0|[1])\d|2[0-3]):(0|[1-5])\d:(0|[1-5])\d$'

        if re.match(r"%s %s" % (date_regex, time_regax), timing):
            eta = datetime.datetime.strptime(timing, "%Y-%m-%d %H:%M:%S")
            t = 'timing'
        #  如果写成+号 可以输入无限长，或考虑前端修改
        elif re.match(r'^\d{1,8}$', timing):
            eta = timing
            t = 'countdown'
        else:
            message = _(u"输入参数%s不符合【秒(s) 或 时间(%%Y-%%m-%%d %%H:%%M:%%S)】格式") % timing
            data.set_outputs('ex_data', message)
            return False
        data.set_outputs('eta', eta)
        data.set_outputs('type', t)

        return True

    def schedule(self, data, parent_data, callback_data=None):
        timing_time = data.get_one_of_outputs('timing_time', default=None)
        if not timing_time:
            eta = data.get_one_of_outputs('eta')
            timing_type = data.get_one_of_outputs('type')
            timing_time = datetime.datetime.now() + datetime.timedelta(
                seconds=int(eta)) if timing_type == 'countdown' else eta
            data.set_outputs('timing_time', timing_time)

        if timing_time <= datetime.datetime.now():
            self.finish_schedule()

        return True

    def outputs_format(self):
        return []


class SleepTimerComponent(Component):
    name = _(u'定时')
    code = 'sleep_timer'
    bound_service = SleepTimerService
    form = settings.STATIC_URL + 'components/atoms/bk/timer.js'
