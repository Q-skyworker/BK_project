# -*- coding: utf-8 -*-
import json

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import ugettext_lazy as _

from gcloud.conf import settings
from gcloud.core.constant import TASK_CATEGORY
from gcloud.core.models import Business
from gcloud.core.utils import convert_readable_username
from gcloud.tasktmpl3.utils import get_notify_receivers

from pipeline.models import PipelineTemplate
from pipeline.core.constants import PE
from pipeline.parser.utils import replace_all_id


FILL_PARAMS_PERM_NAME = 'fill_params'
EXECUTE_TASK_PERM_NAME = 'execute_task'


def get_permission_list():
    permission_list = [
        (FILL_PARAMS_PERM_NAME, _(u"参数填写")),
        (EXECUTE_TASK_PERM_NAME, _(u"任务执行")),
    ]
    return permission_list


def replace_template_id(pipeline_data, reverse=False):
    activities = pipeline_data[PE.activities]
    for act_id, act in activities.iteritems():
        if act['type'] == PE.SubProcess:
            if not reverse:
                act['template_id'] = TaskTemplate.objects.get(pk=act['template_id']).pipeline_template.template_id
            else:
                act['template_id'] = str(TaskTemplate.objects.get(pipeline_template__template_id=act['template_id']).pk)


class TaskTemplateManager(models.Manager):

    @staticmethod
    def create_pipeline_template(**kwargs):
        pipeline_tree = kwargs['pipeline_tree']
        try:
            replace_template_id(pipeline_tree)
        except Exception:
            raise TaskTemplate.DoesNotExist()
        pipeline_template_data = {
            'name': kwargs['name'],
            'creator': kwargs['creator'],
            'description': kwargs['description'],
        }
        pipeline_template = PipelineTemplate.objects.create_model(
            pipeline_tree,
            **pipeline_template_data
        )
        return pipeline_template

    def create(self, **kwargs):
        pipeline_template = self.create_pipeline_template(**kwargs)
        task_template = self.model(
            business=kwargs['business'],
            category=kwargs['category'],
            pipeline_template=pipeline_template,
            notify_type=kwargs['notify_type'],
            notify_receivers=kwargs['notify_receivers'],
            time_out=kwargs['time_out'],
        )
        task_template.save()
        return task_template


class TaskTemplate(models.Model):

    business = models.ForeignKey(Business,
                                 verbose_name=_(u"所属业务"),
                                 blank=True,
                                 null=True,
                                 on_delete=models.SET_NULL)
    category = models.CharField(_(u"模板类型"),
                                choices=TASK_CATEGORY,
                                max_length=255,
                                default='Other')
    pipeline_template = models.ForeignKey(PipelineTemplate,
                                          blank=True,
                                          null=True,
                                          on_delete=models.SET_NULL)
    collector = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       verbose_name=_(u"收藏模板的人"),
                                       blank=True)
    notify_type = models.CharField(_(u"流程事件通知方式"),
                                   max_length=128,
                                   default='[]'
                                   )
    # 形如 json.dumps({'receiver_group': ['Maintainers'], 'more_receiver': 'username1,username2'})
    notify_receivers = models.TextField(_(u"流程事件通知人"),
                                        default='{}'
                                        )
    time_out = models.IntegerField(_(u"流程超时时间(分钟)"),
                                   default=20
                                   )
    is_deleted = models.BooleanField(_(u"是否删除"), default=False)

    objects = TaskTemplateManager()

    def __unicode__(self):
        return u'%s_%s' % (self.business, self.pipeline_template or 'None')

    class Meta:
        verbose_name = _(u"流程模板 TaskTemplate")
        verbose_name_plural = _(u"流程模板 TaskTemplate")
        ordering = ['-id']
        permissions = get_permission_list()

    @property
    def category_name(self):
        return self.get_category_display()

    @property
    def creator_name(self):
        return convert_readable_username(self.pipeline_template.creator)

    @property
    def editor_name(self):
        if self.pipeline_template and self.pipeline_template.editor:
            return convert_readable_username(self.pipeline_template.editor)
        else:
            return ''

    @property
    def name(self):
        return self.pipeline_template.name

    @property
    def create_time(self):
        return self.pipeline_template.create_time

    @property
    def edit_time(self):
        return self.pipeline_template.edit_time or self.create_time

    @property
    def pipeline_tree(self):
        tree = self.pipeline_template.data
        replace_template_id(tree, reverse=True)
        # old data process
        if tree[PE.start_event]['id'][:4] != 'node':
            replace_all_id(tree)
        return tree

    @property
    def template_id(self):
        return str(self.id)

    def get_notify_receivers_list(self, username):
        notify_receivers = json.loads(self.notify_receivers)
        receiver_group = notify_receivers.get('receiver_group', [])
        more_receiver = notify_receivers.get('more_receiver', '')
        receivers = get_notify_receivers(username, self.business.cc_id, receiver_group, more_receiver)
        return receivers

    def update_pipeline_template(self, **kwargs):
        pipeline_template = self.pipeline_template
        if pipeline_template is None:
            return
        pipeline_tree = kwargs.pop('pipeline_tree')
        replace_template_id(pipeline_tree)
        pipeline_template.update_template(pipeline_tree, **kwargs)

    def get_clone_pipeline_tree(self):
        clone_tree = self.pipeline_template.clone_data()
        replace_template_id(clone_tree, reverse=True)
        return clone_tree

    def get_form(self):
        return self.pipeline_template.get_form()

    def get_outputs(self):
        return self.pipeline_template.get_outputs()

    def user_collect(self, username, method):
        user_model = get_user_model()
        user = user_model.objects.get(username=username)
        if method == 'add':
            self.collector.add(user)
        else:
            self.collector.remove(user)
        self.save()
        return {'result': True, 'message': 'success'}
