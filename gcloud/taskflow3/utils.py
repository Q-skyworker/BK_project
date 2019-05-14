# -*- coding: utf-8 -*-
from django.utils import translation

from common.log import logger

from gcloud.core.utils import get_biz_maintainer_info
from gcloud.taskflow3.models import TaskFlowInstance


def get_instance_context(obj):
    try:
        taskflow = TaskFlowInstance.objects.get(pipeline_instance=obj)
    except TaskFlowInstance.DoesNotExist:
        logger.warning('TaskFlowInstance Does not exit: pipeline_template.id=%s' % obj.pk)
        return {}
    operator = obj.executor
    biz_cc_id = taskflow.business.cc_id
    executor, _ = get_biz_maintainer_info(biz_cc_id, operator)
    context = {
        'language': translation.get_language(),
        'biz_cc_id': biz_cc_id,
        'biz_cc_name': taskflow.business.cc_name,
        # 执行任务的操作员
        'operator': operator,
        # 调用ESB接口的执行者
        'executor': executor,
        'task_id': taskflow.id,
        'task_name': taskflow.pipeline_instance.name
    }
    return context
