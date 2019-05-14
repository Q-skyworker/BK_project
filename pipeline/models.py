# -*- coding: utf-8 -*-
import Queue
import ujson as json
import zlib
import hashlib
import logging

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db import models, transaction

from pipeline.utils.uniqid import uniqid, node_uniqid
from pipeline.parser.utils import replace_all_id

MAX_LEN_OF_NAME = 64
logger = logging.getLogger('root')


class CompressJSONField(models.BinaryField):
    def __init__(self, compress_level=6, *args, **kwargs):
        super(CompressJSONField, self).__init__(*args, **kwargs)
        self.compress_level = compress_level

    def get_prep_value(self, value):
        value = super(CompressJSONField, self).get_prep_value(value)
        return zlib.compress(json.dumps(value), self.compress_level)

    def to_python(self, value):
        value = super(CompressJSONField, self).to_python(value)
        return json.loads(zlib.decompress(value))

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)


class SnapshotManager(models.Manager):
    def create_or_get_snapshot(self, data):
        h = hashlib.md5()
        h.update(json.dumps(data))
        snapshot, created = self.get_or_create(md5sum=h.hexdigest())
        if created:
            snapshot.data = data
            snapshot.save()
        return snapshot, created


class Snapshot(models.Model):
    md5sum = models.CharField(_(u"快照字符串的md5sum"), max_length=32, unique=True)
    create_time = models.DateTimeField(_(u"创建时间"), auto_now_add=True)
    data = CompressJSONField(null=True, blank=True)  # 前端画布数据

    objects = SnapshotManager()

    class Meta:
        verbose_name = _(u"模板快照")
        verbose_name_plural = _(u"模板快照")
        ordering = ['-id']
        app_label = 'pipeline'

    def __unicode__(self):
        return unicode(self.md5sum)

    def has_change(self, data):
        h = hashlib.md5()
        h.update(json.dumps(data))
        md5 = h.hexdigest()
        return md5, self.md5sum != md5


def get_subprocess_act_list(pipeline_data):
    activities = pipeline_data['activities']
    act_ids = filter(lambda act_id: activities[act_id]['type'] == 'SubProcess', activities)
    return [activities[act_id] for act_id in act_ids]


class TemplateManager(models.Manager):
    def create_model(self, structure_data, **kwargs):
        snapshot, _ = Snapshot.objects.create_or_get_snapshot(structure_data)
        kwargs['snapshot'] = snapshot
        kwargs['template_id'] = node_uniqid()
        return self.create(**kwargs)

    def delete_model(self, template_ids):
        if not isinstance(template_ids, list):
            template_ids = [template_ids]
        qs = self.filter(template_id__in=template_ids)
        for template in qs:
            template.is_deleted = True
            template.name = uniqid()
            template.save()

    def construct_subprocess_ref_graph(self, pipeline_data, root_id=None, root_name=None):
        subprocess_act = get_subprocess_act_list(pipeline_data)
        tid_queue = Queue.Queue()
        graph = {}
        name_map = {}

        if root_id:
            graph[root_id] = [act['template_id'] for act in subprocess_act]
            name_map[root_id] = root_name

        for act in subprocess_act:
            tid_queue.put(act['template_id'])

        while not tid_queue.empty():
            tid = tid_queue.get()
            template = self.get(template_id=tid)
            name_map[tid] = template.name
            subprocess_act = get_subprocess_act_list(template.data)

            for act in subprocess_act:
                ref_tid = act['template_id']
                graph.setdefault(tid, []).append(ref_tid)
                if ref_tid not in graph:
                    tid_queue.put(ref_tid)
            if not subprocess_act:
                graph[tid] = []

        return graph, name_map


class PipelineTemplate(models.Model):
    template_id = models.CharField(_(u'模板ID'), max_length=32, unique=True)
    name = models.CharField(_(u'模板名称'), max_length=MAX_LEN_OF_NAME, default='default_template')
    create_time = models.DateTimeField(_(u'创建时间'), auto_now_add=True)
    creator = models.CharField(_(u'创建者'), max_length=32)
    description = models.TextField(_(u'描述'), null=True, blank=True)
    editor = models.CharField(_(u'修改者'), max_length=32, null=True, blank=True)
    edit_time = models.DateTimeField(_(u'修改时间'), auto_now=True)
    snapshot = models.ForeignKey(Snapshot, verbose_name=_(u'模板结构数据'))
    is_deleted = models.BooleanField(
        _(u'是否删除'),
        default=False,
        help_text=_(u'表示当前模板是否删除')
    )

    objects = TemplateManager()

    class Meta:
        verbose_name = _(u'Pipeline模板')
        verbose_name_plural = _(u'Pipeline模板')
        ordering = ['-edit_time']
        app_label = 'pipeline'

    def __unicode__(self):
        return '%s-%s' % (self.template_id, self.name)

    @property
    def data(self):
        return self.snapshot.data

    def clone_data(self):
        data = self.data
        replace_all_id(self.data)
        return data

    def update_template(self, structure_data, **kwargs):
        snapshot, _ = Snapshot.objects.create_or_get_snapshot(structure_data)
        kwargs['snapshot'] = snapshot
        kwargs['edit_time'] = timezone.now()
        exclude_keys = ['template_id', 'creator', 'create_time', 'is_deleted']
        for key in exclude_keys:
            kwargs.pop(key, None)
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        self.save()

    def get_form(self):
        data = self.data
        form = {}
        for key, var_info in data['constants'].iteritems():
            if var_info['show_type'] == 'show':
                form[key] = var_info
        return form

    def get_outputs(self):
        data = self.data
        outputs_key = data['outputs']
        outputs = {}
        for key in outputs_key:
            if key in data['constants']:
                outputs[key] = data['constants'][key]
        return outputs


class TemplateScheme(models.Model):
    template = models.ForeignKey(PipelineTemplate, verbose_name=_(u"对应模板 ID"), null=False, blank=False)
    unique_id = models.CharField(_(u"方案唯一ID"), max_length=97, unique=True, null=False, blank=True)
    name = models.CharField(_(u"方案名称"), max_length=64, null=False, blank=False)
    edit_time = models.DateTimeField(_(u"修改时间"), auto_now=True)
    data = CompressJSONField(verbose_name=_(u"方案数据"))


def unfold_subprocess(pipeline_data):
    replace_all_id(pipeline_data)
    activities = pipeline_data['activities']
    for act_id, act in activities.iteritems():
        if act['type'] == 'SubProcess':
            subproc_data = PipelineTemplate.objects.get(template_id=act['template_id']).data
            constants_inputs = act.pop('constants')
            # replace show constants with inputs
            for key, info in constants_inputs.iteritems():
                if 'form' in info:
                    info.pop('form')
                subproc_data['constants'][key] = info
            unfold_subprocess(subproc_data)

            subproc_data['id'] = act_id
            act['pipeline'] = subproc_data


class InstanceManager(models.Manager):

    def create_instance(self, template, exec_data, **kwargs):
        unfold_subprocess(exec_data)
        instance_id = node_uniqid()
        exec_data['id'] = instance_id
        exec_snapshot, _ = Snapshot.objects.create_or_get_snapshot(exec_data)
        kwargs['template'] = template
        kwargs['instance_id'] = instance_id
        kwargs['snapshot_id'] = template.snapshot.id
        kwargs['execution_snapshot_id'] = exec_snapshot.id
        return self.create(**kwargs)

    def delete_model(self, instance_ids):
        if not isinstance(instance_ids, list):
            instance_ids = [instance_ids]
        qs = self.filter(instance_id__in=instance_ids)
        for instance in qs:
            instance.is_deleted = True
            instance.name = uniqid()
            instance.save()

    def set_started(self, instance_id, executor):
        with transaction.atomic():
            instance = self.select_for_update().get(instance_id=instance_id)
            if instance.is_started:
                return False
            instance.start_time = timezone.now()
            instance.is_started = True
            instance.executor = executor
            instance.save()
        return True

    def set_finished(self, instance_id):
        with transaction.atomic():
            try:
                instance = self.select_for_update().get(instance_id=instance_id)
            except PipelineInstance.DoesNotExist:
                return None
            instance.finish_time = timezone.now()
            instance.is_finished = True
            instance.save()
        return instance


class PipelineInstance(models.Model):
    template = models.ForeignKey(PipelineTemplate, verbose_name=_(u'Pipeline模板'))
    instance_id = models.CharField(_(u'实例ID'), max_length=32, unique=True)
    name = models.CharField(_(u'实例名称'), max_length=MAX_LEN_OF_NAME, default='default_instance')
    creator = models.CharField(_(u'创建者'), max_length=32, blank=True)
    create_time = models.DateTimeField(_(u'创建时间'), auto_now_add=True)
    executor = models.CharField(_(u'执行者'), max_length=32, blank=True)
    start_time = models.DateTimeField(_(u'启动时间'), null=True, blank=True)
    finish_time = models.DateTimeField(_(u'结束时间'), null=True, blank=True)
    description = models.TextField(_(u'描述'), blank=True)
    is_started = models.BooleanField(_(u'是否已经启动'), default=False)
    is_finished = models.BooleanField(_(u'是否已经完成'), default=False)
    is_deleted = models.BooleanField(
        _(u'是否已经删除'),
        default=False,
        help_text=_(u'表示当前实例是否删除')
    )
    snapshot = models.ForeignKey(
        Snapshot,
        related_name='snapshot',
        verbose_name=_(u'实例结构数据')
    )
    execution_snapshot = models.ForeignKey(
        Snapshot, null=True,
        related_name='execution_snapshot',
        verbose_name=_(u'用于实例执行的结构数据')
    )

    objects = InstanceManager()

    class Meta:
        verbose_name = _(u'Pipeline实例')
        verbose_name_plural = _(u'Pipeline实例')
        ordering = ['-create_time']
        app_label = 'pipeline'

    def __unicode__(self):
        return '%s-%s' % (self.instance_id, self.name)

    @property
    def data(self):
        return self.snapshot.data

    @property
    def execution_data(self):
        return self.execution_snapshot.data

    def set_execution_data(self, data):
        self.execution_snapshot.data = data
        self.execution_snapshot.save()

    def _replace_id(self, exec_data):
        replace_all_id(exec_data)
        activities = exec_data['activities']
        for act_id, act in activities.iteritems():
            if act['type'] == 'SubProcess':
                self._replace_id(act['pipeline'])
                act['pipeline']['id'] = act_id

    def clone(self, creator):
        # name = self.name[10:] if len(self.name) >= MAX_LEN_OF_NAME - 10 else self.name
        name = timezone.now().strftime('clone%Y%m%d%H%m%S')
        instance_id = node_uniqid()

        exec_data = self.execution_data
        self._replace_id(exec_data)
        # replace root id
        exec_data['id'] = instance_id
        new_snapshot, _ = Snapshot.objects.create_or_get_snapshot(exec_data)

        return self.__class__.objects.create(template=self.template, instance_id=instance_id,
                                             name=name, creator=creator,
                                             description=self.description, snapshot=self.snapshot,
                                             execution_snapshot=new_snapshot)

    def start(self, executor):
        from pipeline.parser import pipeline_parser
        from pipeline.engine import api
        from pipeline.utils.context import get_pipeline_context

        with transaction.atomic():
            instance = self.__class__.objects.select_for_update().get(id=self.id)
            if instance.is_started:
                return False, 'pipeline instance already started.'
            instance.start_time = timezone.now()
            instance.is_started = True
            instance.executor = executor

            pipeline_data = instance.execution_data
            parser = pipeline_parser.WebPipelineAdapter(pipeline_data)
            pipeline = parser.parser(get_pipeline_context(instance, 'instance'))

            instance.save()

        api.start_pipeline(pipeline)

        return True, {}


class VariableModel(models.Model):
    """
    注册的变量
    """
    code = models.CharField(_(u"变量编码"), max_length=255, unique=True)
    status = models.BooleanField(_(u"变量是否可用"), default=True)

    class Meta:
        verbose_name = _(u"Variable变量")
        verbose_name_plural = _(u"Variable变量")
        ordering = ['-id']
        app_label = 'pipeline'

    def __unicode__(self):
        return self.code
