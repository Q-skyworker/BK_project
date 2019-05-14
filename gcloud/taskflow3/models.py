# -*- coding: utf-8 -*-
import json
import logging

import re
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _

from common.log import logger
from blueapps.utils import managermixins
from gcloud.conf import settings
from gcloud.core.constant import TASK_FLOW_TYPE, TASK_CATEGORY
from gcloud.core.models import Business
from gcloud.core.utils import convert_readable_username, strftime_with_timezone, get_client_by_user_and_biz_id
from gcloud.tasktmpl3.models import TaskTemplate, replace_template_id
from gcloud.taskflow3.constants import TASK_CREATE_METHOD
from gcloud.taskflow3.signals import taskflow_started

from pipeline.core.constants import PE
from pipeline.component_framework import library
from pipeline.component_framework.constant import ConstantPool
from pipeline.models import PipelineInstance
from pipeline.engine import exceptions
from pipeline.engine import api as pipeline_api
from pipeline.engine.models import Data
from pipeline.parser import pipeline_parser
from pipeline.utils.context import get_pipeline_context
from pipeline.engine import states


INSTANCE_ACTIONS = {
    'start': None,
    'pause': pipeline_api.pause_pipeline,
    'resume': pipeline_api.resume_pipeline,
    'revoke': pipeline_api.revoke_pipeline
}

NODE_ACTIONS = {
    'revoke': pipeline_api.resume_node_appointment,
    'retry': pipeline_api.retry_node,
    'skip': pipeline_api.skip_node,
    'callback': pipeline_api.activity_callback,
    'skip_exg': pipeline_api.skip_exclusive_gateway,
    'pause': pipeline_api.pause_node_appointment,
    'resume': pipeline_api.resume_node_appointment,
    'pause_subproc': pipeline_api.pause_pipeline,
    'resume_subproc': pipeline_api.resume_node_appointment,
}


class TaskFlowInstanceManager(models.Manager, managermixins.ClassificationCountMixin):
    @staticmethod
    def create_pipeline_instance(template, **kwargs):
        pipeline_tree = kwargs['pipeline_tree']
        replace_template_id(pipeline_tree)
        pipeline_template_data = {
            'name': kwargs['name'],
            'creator': kwargs['creator'],
            'description': kwargs.get('description', ''),
        }
        pipeline_instance = PipelineInstance.objects.create_instance(
            template.pipeline_template,
            pipeline_tree,
            **pipeline_template_data
        )
        return pipeline_instance

    @staticmethod
    def create_pipeline_instance_exclude_task_nodes(template, task_info, constants=None, exclude_task_nodes_id=None):
        """
        @param template:
        @param task_info: {
            'name': '',
            'creator': '',
            'description': '',
        }
        @param constants: 覆盖参数，如 {'${a}': '1', '${b}': 2}
        @param exclude_task_nodes_id: 取消执行的可选节点
        @return:
        """
        if constants is None:
            constants = {}
        pipeline_tree = template.pipeline_tree

        try:
            TaskFlowInstanceManager.preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id)
        except Exception as e:
            return False, e.message

        # change constants
        for key, value in constants.items():
            if key in pipeline_tree[PE.constants]:
                pipeline_tree[PE.constants][key]['value'] = value

        task_info['pipeline_tree'] = pipeline_tree
        pipeline_inst = TaskFlowInstanceManager.create_pipeline_instance(template, **task_info)

        return True, pipeline_inst

    @staticmethod
    def preview_pipeline_tree_exclude_task_nodes(pipeline_tree, exclude_task_nodes_id=None):
        if exclude_task_nodes_id is None:
            exclude_task_nodes_id = []

        locations = {item['id']: item for item in pipeline_tree.get(PE.location, [])}
        lines = {item['id']: item for item in pipeline_tree.get(PE.line, [])}

        for task_node_id in exclude_task_nodes_id:
            if task_node_id not in pipeline_tree[PE.activities]:
                error = 'task node[id=%s] is not in template pipeline tree' % task_node_id
                raise Exception(error)

            task_node = pipeline_tree[PE.activities].pop(task_node_id)
            if not task_node['optional']:
                error = 'task node[id=%s] is not optional' % task_node_id
                raise Exception(error)

            # change next_node's incoming: task node、control node is different
            # change incoming_flow's target to next node
            # delete outgoing_flow
            incoming_id, outgoing_id = task_node[PE.incoming], task_node[PE.outgoing]
            incoming_flow = pipeline_tree[PE.flows][incoming_id]
            outgoing_flow = pipeline_tree[PE.flows][outgoing_id]
            target_id = outgoing_flow[PE.target]

            if target_id in pipeline_tree[PE.activities]:
                next_node = pipeline_tree[PE.activities][target_id]
                next_node[PE.incoming] = incoming_id
            elif target_id in pipeline_tree[PE.gateways]:
                next_node = pipeline_tree[PE.gateways][target_id]
                if next_node['type'] in [PE.ExclusiveGateway, PE.ParallelGateway]:
                    next_node[PE.incoming] = incoming_id
                # PE.ConvergeGateway
                else:
                    next_node[PE.incoming].pop(next_node[PE.incoming].index(outgoing_id))
                    next_node[PE.incoming].append(incoming_id)
            # PE.end_event
            else:
                next_node = pipeline_tree[PE.end_event]
                next_node[PE.incoming] = incoming_id

            incoming_flow[PE.target] = next_node['id']

            pipeline_tree[PE.flows].pop(outgoing_id)

            # web location data
            try:
                locations.pop(task_node_id)
                lines.pop(outgoing_id)
                lines[incoming_id][PE.target]['id'] = next_node['id']
            except Exception as e:
                logger.exception('create_pipeline_instance_exclude_task_nodes adjust web data error:%s' % e)

        pipeline_tree[PE.line] = lines.values()
        pipeline_tree[PE.location] = locations.values()

        # pop unreferenced constant
        data = {}
        for task_node_id, task_node in pipeline_tree[PE.activities].items():
            if task_node['type'] == PE.ServiceActivity:
                node_data = {('%s_%s' % (task_node_id, key)): value
                             for key, value in task_node['component']['data'].items()}
            # PE.SubProcess
            else:
                node_data = {('%s_%s' % (task_node_id, key)): value
                             for key, value in task_node['constants'].items() if value['show_type'] == 'show'}
            data.update(node_data)

        for gw_id, gw in pipeline_tree[PE.gateways].items():
            if gw['type'] == PE.ExclusiveGateway:
                gw_data = {('%s_%s' % (gw_id, key)): {'value': value['evaluate']}
                           for key, value in gw['conditions'].items()}
                data.update(gw_data)

        constants = pipeline_tree[PE.constants]
        referenced_constants = []
        while True:
            last_count = len(referenced_constants)
            pool = ConstantPool(data)
            refs = pool.get_reference_info(strict=False)
            for _, keys in refs.items():
                for key in keys:
                    if key in constants and key not in referenced_constants:
                        referenced_constants.append(key)
                        data.update({key: constants[key]})
            if len(referenced_constants) == last_count:
                break
            last_count = len(referenced_constants)

        # rebuild constants index
        referenced_constants.sort(key=lambda x: constants[x]['index'])
        new_constants = {}
        for index, key in enumerate(referenced_constants):
            value = constants[key]
            value['index'] = index
            # delete constant reference info  to task node
            for task_node_id in exclude_task_nodes_id:
                if task_node_id in value['source_info']:
                    value['source_info'].pop(task_node_id)
            new_constants[key] = value
        pipeline_tree[PE.constants] = new_constants

        return

    def extend_classified_count(self, group_by, filters=None):
        """
        @summary: 兼容按照任务状态分类的扩展
        @param group_by:
        @param filters:
        @return:
        """
        if filters is None:
            filters = {}
        pipeline_inst_regex = re.compile(r'^[name|create_time|creator|create_time|executor|'
                                         r'start_time|finish_time|is_started|is_finished]')
        prefix_filters = {}
        for cond in filters:
            if pipeline_inst_regex.match(cond):
                filter_cond = 'pipeline_instance__%s' % cond
            else:
                filter_cond = cond
            prefix_filters.update({filter_cond: filters[cond]})

        if group_by == 'status':
            try:
                taskflow = self.filter(**prefix_filters)
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
            total = taskflow.count()
            groups = [
                {
                    'code': 'CREATED',
                    'name': _(u"未执行"),
                    'value': taskflow.filter(pipeline_instance__is_started=False).count()
                },
                {
                    'code': 'EXECUTING',
                    'name': _(u"执行中"),
                    'value': taskflow.filter(pipeline_instance__is_started=True,
                                             pipeline_instance__is_finished=False).count()
                },
                {
                    'code': 'FINISHED',
                    'name': _(u"已完成"),
                    'value': taskflow.filter(pipeline_instance__is_finished=True).count()
                }
            ]
        elif group_by in ['category', 'create_method', 'flow_type']:
            try:
                total, groups = self.classified_count(prefix_filters, group_by)
            except Exception as e:
                message = u"query_task_list params conditions[%s] have invalid key or value: %s" % (filters, e)
                return False, message
        else:
            total, groups = 0, []
        data = {'total': total, 'groups': groups}
        return True, data


class TaskFlowInstance(models.Model):
    business = models.ForeignKey(Business,
                                 verbose_name=_(u"业务"),
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL)
    pipeline_instance = models.ForeignKey(PipelineInstance,
                                          blank=True,
                                          null=True,
                                          on_delete=models.SET_NULL)
    category = models.CharField(_(u"任务类型，继承自模板"), choices=TASK_CATEGORY,
                                max_length=255, default='Other')
    template_id = models.CharField(_(u"创建任务所用的模板ID"), max_length=255)
    create_method = models.CharField(_(u"创建方式"),
                                     max_length=30,
                                     choices=TASK_CREATE_METHOD,
                                     default='app')
    create_info = models.CharField(_(u"创建任务额外信息（App maker ID或者APP CODE）"),
                                   max_length=255, blank=True)
    flow_type = models.CharField(_(u"任务流程类型"),
                                 max_length=255,
                                 choices=TASK_FLOW_TYPE,
                                 default='common')
    current_flow = models.CharField(_(u"当前任务流程阶段"), max_length=255)
    is_deleted = models.BooleanField(_(u"是否删除"), default=False)

    objects = TaskFlowInstanceManager()

    def __unicode__(self):
        return u"%s_%s" % (self.business, self.pipeline_instance.name)

    class Meta:
        verbose_name = _(u"流程实例 TaskFlowInstance")
        verbose_name_plural = _(u"流程实例 TaskFlowInstance")
        ordering = ['-id']

    @property
    def instance_id(self):
        return self.id

    @property
    def category_name(self):
        return self.get_category_display()

    @property
    def creator(self):
        return self.pipeline_instance.creator

    @property
    def creator_name(self):
        return convert_readable_username(self.creator)

    @property
    def executor(self):
        return self.pipeline_instance.executor

    @property
    def executor_name(self):
        return convert_readable_username(self.executor)

    @property
    def pipeline_tree(self):
        return self.pipeline_instance.execution_data

    @property
    def name(self):
        return self.pipeline_instance.name

    @property
    def create_time(self):
        return self.pipeline_instance.create_time

    @property
    def start_time(self):
        return self.pipeline_instance.start_time

    @property
    def finish_time(self):
        return self.pipeline_instance.finish_time

    @property
    def is_started(self):
        return self.pipeline_instance.is_started

    @property
    def is_finished(self):
        return self.pipeline_instance.is_finished

    @property
    def template(self):
        return TaskTemplate.objects.get(pk=self.template_id)

    @property
    def url(self):
        if settings.RUN_MODE == 'PRODUCT':
            prefix = settings.APP_HOST
        else:
            prefix = settings.TEST_APP_HOST
        return '%s/taskflow/detail/%s/?instance_id=%s' % (prefix, self.business.cc_id, self.id)

    @staticmethod
    def format_pipeline_status(status_tree):
        """
        @summary: 转换通过 pipeline api 获取的任务状态格式
        @return:
        """
        status_tree.setdefault('children', {})
        status_tree.pop('created_time', '')
        status_tree['start_time'] = strftime_with_timezone(status_tree.pop('started_time'))
        status_tree['finish_time'] = strftime_with_timezone(status_tree.pop('archived_time'))
        child_status = []
        for identifier_code, child_tree in status_tree['children'].iteritems():
            TaskFlowInstance.format_pipeline_status(child_tree)
            child_status.append(child_tree['state'])

        if status_tree['state'] == states.BLOCKED:
            if states.RUNNING in child_status:
                status_tree['state'] = states.RUNNING
            elif states.FAILED in child_status:
                status_tree['state'] = states.FAILED
            elif states.SUSPENDED in child_status or 'NODE_SUSPENDED' in child_status:
                status_tree['state'] = 'NODE_SUSPENDED'
            # 子流程 BLOCKED 状态表示子节点失败
            elif not child_status:
                status_tree['state'] = states.FAILED

    def get_status(self):
        if not self.pipeline_instance.is_started:
            return {
                "start_time": None,
                "state": "CREATED",
                "retry": 0,
                "skip": 0,
                "finish_time": None,
                "children": {}
            }
        status_tree = pipeline_api.get_status_tree(self.pipeline_instance.instance_id, max_depth=99)
        TaskFlowInstance.format_pipeline_status(status_tree)
        return status_tree

    def get_act_data(self, act_id, component_code=None, subprocess_stack=None):
        act_started = True
        result = True
        try:
            inputs = pipeline_api.get_inputs(act_id)
            outputs = pipeline_api.get_outputs(act_id)
        except Data.DoesNotExist:
            act_started = False

        if component_code:
            if not act_started:
                try:
                    instance_data = self.pipeline_instance.execution_data
                    inputs = pipeline_parser.WebPipelineAdapter(instance_data).get_act_inputs(
                        act_id=act_id,
                        subprocess_stack=subprocess_stack,
                        root_pipeline_data=get_pipeline_context(self.pipeline_instance, 'instance')
                    )
                    outputs = {}
                except Exception as e:
                    inputs = {}
                    result = False
                    message = 'parser pipeline tree error: %s' % e
                    logger.exception(message)
                    outputs = {'ex_data': message}

            outputs_table = []
            try:
                component = library.ComponentLibrary.get_component_class(component_code)
                outputs_format = component.outputs_format()
            except Exception as e:
                result = False
                message = 'get component[component_code=%s] format error: %s' % (component_code, e)
                logger.exception(message)
                outputs = {'ex_data': message}
            else:
                for outputs_item in outputs_format:
                    value = outputs.get('outputs', {}).get(outputs_item['key'], '')
                    outputs_table.append({
                        'name': outputs_item['name'],
                        'value': value
                    })
        else:
            outputs_table = []

        data = {
            'inputs': inputs,
            'outputs': outputs_table,
            'ex_data': outputs.pop('ex_data', '')
        }
        return {'result': result, 'data': data, 'message': data['ex_data']}

    def get_act_detail(self, act_id, component_code=None, subprocess_stack=None):
        try:
            detail = pipeline_api.get_status_tree(act_id)
        except exceptions.InvalidOperationException as e:
            return {'result': False, 'message': e.message}
        TaskFlowInstance.format_pipeline_status(detail)
        data = self.get_act_data(act_id, component_code, subprocess_stack)
        if not data['result']:
            return data
        detail['histories'] = pipeline_api.get_activity_histories(act_id)
        for his in detail['histories']:
            his.setdefault('state', 'FAILED')
            TaskFlowInstance.format_pipeline_status(his)
        detail.update(data['data'])
        return {'result': True, 'data': detail}

    def user_has_perm(self, user, flow_list):
        """
        @summary: 判断用户是否有操作当前流程权限
        @param user:
        @param flow_list:['fill_params', 'execute_task']
        @return:
        """
        user_has_right = False
        try:
            business = self.business
            template = TaskTemplate.objects.get(pk=self.template_id)
            if user.is_superuser or user.has_perm('manage_business', business):
                user_has_right = True
            else:
                for flow in flow_list:
                    perm_name = flow
                    if user.has_perm(perm_name, template):
                        user_has_right = True
                        break
        except Exception as e:
            logger.exception(u"TaskFlowInstance user_has_perm exception, error=%s" % e)
        return user_has_right

    def task_claim(self, username, constants, name):
        if self.flow_type != 'common_func':
            result = {
                'result': False,
                'messgae': 'task is not functional'
            }
        elif self.current_flow != 'func_claim':
            result = {
                'result': False,
                'messgae': 'task with current_flow:%s cannot be claimed' % self.current_flow
            }
        else:
            with transaction.atomic():
                self.reset_pipeline_instance_data(constants, name)
                result = self.function_task.get(task=self).claim_task(username)
                if result['result']:
                    self.current_flow = 'execute_task'
                    self.save()
        return result

    def task_action(self, action, username):
        if self.current_flow != 'execute_task':
            return {'result': False, 'message': 'task with current_flow:%s cannot be %sed' % (self.current_flow,
                                                                                              action)}
        if action not in INSTANCE_ACTIONS:
            return {'result': False, 'message': 'task action is invalid'}
        if action == 'start':
            try:
                success, data = self.pipeline_instance.start(username)
                if success:
                    taskflow_started.send(sender=self, username=username)
                return {'result': success, 'data': data, 'message': data}
            except Exception as e:
                message = u"task[id=%s] action failed:%s" % (self.id, e)
                logger.exception(message)
                return {'result': False, 'message': message}
        try:
            success = INSTANCE_ACTIONS[action](self.pipeline_instance.instance_id)
            if success:
                return {'result': True, 'data': {}}
            else:
                return {'result': False, 'message': 'operate failed, please try again later'}
        except Exception as e:
            message = u"task[id=%s] action failed:%s" % (self.id, e)
            logger.exception(message)
            return {'result': False, 'message': message}

    def nodes_action(self, action, node_id, username, **kwargs):
        # TODO assert node_id is sub_node of pipeline
        if action not in NODE_ACTIONS:
            return {'result': False, 'message': 'task action is invalid'}
        try:
            if action == 'callback':
                success = NODE_ACTIONS[action](node_id, kwargs['data'])
            elif action == 'skip_exg':
                success = NODE_ACTIONS[action](node_id, kwargs['flow_id'])
            elif action == 'retry':
                success = NODE_ACTIONS[action](node_id, kwargs['inputs'])
            else:
                success = NODE_ACTIONS[action](node_id)
        except Exception as e:
            message = u"task[id=%s] node[id=%s] action failed:%s" % (self.id, node_id, e)
            logger.exception(message)
            return {'result': False, 'message': message}
        if success:
            return {'result': True, 'data': 'success'}
        else:
            return {'result': False, 'message': 'operate failed, please try again later'}

    def clone(self, username, **kwargs):
        clone_pipeline = self.pipeline_instance.clone(username)
        self.pk = None
        self.pipeline_instance = clone_pipeline
        if 'create_method' in kwargs:
            self.create_method = kwargs['create_method']
            self.create_info = kwargs.get('create_info', '')
        if self.flow_type == 'common_func':
            self.current_flow = 'func_claim'
        else:
            self.current_flow = 'execute_task'
        self.is_deleted = False
        self.save()
        return self.pk

    def reset_pipeline_instance_data(self, constants, name):
        exec_data = self.pipeline_tree
        try:
            for key, value in constants.iteritems():
                if key in exec_data['constants']:
                    exec_data['constants'][key]['value'] = value
            self.pipeline_instance.set_execution_data(exec_data)
            if name:
                self.pipeline_instance.name = name
                self.pipeline_instance.save()
        except Exception as e:
            logger.exception('TaskFlow reset_pipeline_instance_data error:id=%s, constants=%s, error=%s' % (
                self.pk, json.dumps(constants), e))
            return {'result': False, 'message': 'constants is not valid'}
        return {'result': True, 'data': 'success'}

    def spec_nodes_timer_reset(self, node_id, username, inputs):
        # TODO assert node_id is sub_node of pipeline
        success = pipeline_api.forced_fail(node_id)
        if not success:
            return {'result': False, 'message': 'timer node not exits or is finished'}
        success = pipeline_api.retry_node(node_id, inputs)
        if not success:
            return {'result': False, 'message': 'reset timer failed, please try again later'}
        return {'result': True, 'data': 'success'}

    def get_act_web_info(self, act_id):

        def get_act_of_pipeline(pipeline_tree):
            for node_id, node_info in pipeline_tree['activities'].items():
                if node_id == act_id:
                    return node_info
                elif node_info['type'] == 'SubProcess':
                    return get_act_of_pipeline(node_info['pipeline'])

        return get_act_of_pipeline(self.pipeline_tree)

    def send_message(self, msg_type, atom_node_name=''):
        template = self.template
        pipeline_inst = self.pipeline_instance
        executor = pipeline_inst.executor

        notify_type = json.loads(template.notify_type)
        receivers_list = template.get_notify_receivers_list(executor)
        receivers = ','.join(receivers_list)

        if msg_type == 'atom_failed':
            title = _(u"【标准运维APP通知】执行失败")
            content = _(u"您在【{cc_name}】业务中的任务【{task_name}】执行失败，当前失败节点是【{node_name}】，"
                        u"操作员是【{executor}】，请前往标准运维APP({url})查看详情！").format(
                cc_name=self.business.cc_name,
                task_name=pipeline_inst.name,
                node_name=atom_node_name,
                executor=executor,
                url=self.url
            )
        elif msg_type == 'task_finished':
            title = _(u"【标准运维APP通知】执行完成")
            content = _(u"您在【{cc_name}】业务中的任务【{task_name}】执行成功，操作员是【{executor}】，"
                        u"请前往标准运维APP({url})查看详情！").format(
                cc_name=self.business.cc_name,
                task_name=pipeline_inst.name,
                executor=executor,
                url=self.url
            )
        else:
            return False

        client = get_client_by_user_and_biz_id(executor, self.business.cc_id)
        if 'weixin' in notify_type:
            kwargs = {
                'receiver__username': receivers,
                'data': {
                    'heading': title,
                    'message': content,
                }
            }
            result = client.cmsi.send_weixin(kwargs)
            if not result['result']:
                logger.error('taskflow send weixin, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                             json.dumps(result)))
        if 'sms' in notify_type:
            kwargs = {
                'receiver__username': receivers,
                'content': u"%s\n%s" % (title, content),
            }
            result = client.cmsi.send_sms(kwargs)
            if not result['result']:
                logger.error('taskflow send sms, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                          json.dumps(result)))

        if 'mail' in notify_type:
            kwargs = {
                'receiver__username': receivers,
                'title': title,
                'content': content,
            }
            result = client.cmsi.send_mail(kwargs)
            if not result['result']:
                logger.error('taskflow send mail, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                           json.dumps(result)))

        if 'voice' in notify_type:
            kwargs = {
                'receiver__username': receivers,
                'auto_read_message': u"%s\n%s" % (title, content),
            }
            result = client.cmsi.send_voice_msg(kwargs)
            if not result['result']:
                logger.error('taskflow send voice, kwargs=%s, result=%s' % (json.dumps(kwargs),
                                                                            json.dumps(result)))

        return True
