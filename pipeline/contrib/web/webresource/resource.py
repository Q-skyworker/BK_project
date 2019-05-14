# -*- coding: utf-8 -*-
import ujson as json

from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from tastypie.resources import ModelResource, ALL_WITH_RELATIONS
from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from tastypie.validation import FormValidation
from tastypie.exceptions import ImmediateHttpResponse

from pipeline import exceptions
from pipeline.models import PipelineTemplate, Snapshot, PipelineInstance, unfold_subprocess, TemplateScheme
from pipeline.utils.graph import Graph
from pipeline.utils.uniqid import uniqid, node_uniqid
from pipeline.component_framework.models import ComponentModel
from pipeline.component_framework.library import ComponentLibrary
from pipeline.contrib.web import forms
from pipeline.validators.utils import validate_converge_gateway


def raise_validation_error(resource, bundle, resource_name, field, message):
    bundle.errors = {
        resource_name: {
            field: [
                message
            ]
        }
    }
    raise ImmediateHttpResponse(response=resource.error_response(bundle.request, bundle.errors))


class PipelineSerializer(Serializer):

    def format_datetime(self, data):
        if timezone.is_aware(data):
            data = timezone.localtime(data)
        return data.strftime('%Y-%m-%d %H:%M:%S')


class SnapshotResource(ModelResource):
    class Meta:
        queryset = Snapshot.objects.all()


class PipelineTemplateResource(ModelResource):
    data = fields.ForeignKey(SnapshotResource, 'snapshot')

    class Meta:
        queryset = PipelineTemplate.objects.filter(is_deleted=False)
        resource_name = 'templates'
        excludes = ['is_deleted']
        always_return_data = True
        detail_uri_name = 'template_id'
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'patch', 'post', 'delete']
        filtering = {
            'template_id': ALL_WITH_RELATIONS,
        }

        authorization = Authorization()
        serializer = PipelineSerializer()
        validation = FormValidation(form_class=forms.PipelineTemplateForm)

    def dehydrate_data(self, bundle):
        return json.dumps(bundle.obj.snapshot.data)

    def hydrate(self, bundle):
        pop_keys = ['template_id', 'create_time', 'edit_time']
        for key in pop_keys:
            if key in bundle.data:
                bundle.data.pop(key)

        return super(PipelineTemplateResource, self).hydrate(bundle)

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        json_data = bundle.data['data']
        try:
            data = json.loads(json_data)
        except Exception:
            raise_validation_error(self, bundle,
                                   'templates', 'data', _(u"JSON 格式不合法"))

        self.subprocess_ref_validate(bundle, data, root_id=bundle.obj.template_id, root_name=bundle.obj.name)
        self.gateway_validate(bundle, data)

        bundle.obj.snapshot, _ = Snapshot.objects.create_or_get_snapshot(data)
        bundle.data.pop('data')
        return super(PipelineTemplateResource, self).obj_update(bundle, skip_errors=skip_errors, **kwargs)

    def obj_create(self, bundle, **kwargs):
        json_data = bundle.data.get('data')
        try:
            data = json.loads(json_data)
        except Exception:
            raise_validation_error(self, bundle, 'templates', 'data', _(u"JSON 格式不合法"))

        self.subprocess_ref_validate(bundle, data)
        self.gateway_validate(bundle, data)

        snapshot, _ = Snapshot.objects.create_or_get_snapshot(data)
        kwargs['snapshot_id'] = snapshot.id
        kwargs['template_id'] = node_uniqid()
        # must pop data field after the creation of snapshot is finished.
        bundle.data.pop('data')

        return super(PipelineTemplateResource, self).obj_create(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        template_id = kwargs['template_id']
        PipelineTemplate.objects.delete_model(template_id)

    def alter_list_data_to_serialize(self, request, data):
        for bundle in data['objects']:
            bundle.data.pop('id')
            bundle.data.pop('data')
            bundle.data.pop('description')

        return data

    def alter_detail_data_to_serialize(self, request, data):
        bundle = data
        bundle.data.pop('id')

        return data

    def subprocess_ref_validate(self, bundle, data, root_id=None, root_name=None):
        try:
            sub_refs, name_map = PipelineTemplate.objects.construct_subprocess_ref_graph(data, root_id=root_id,
                                                                                      root_name=root_name)
        except PipelineTemplate.DoesNotExist as e:
            raise_validation_error(self, bundle,
                                   'templates', 'data', e.message)

        nodes = sub_refs.keys()
        flows = []
        for node in nodes:
            for ref in sub_refs[node]:
                if ref in nodes:
                    flows.append([node, ref])
        graph = Graph(nodes, flows)
        # circle reference check
        trace = graph.get_cycle()
        if trace:
            name_trace = ' -> '.join(map(lambda proc_id: name_map[proc_id], trace))
            raise_validation_error(self, bundle,
                                   'templates', 'data', _(u"子流程引用链中存在循环引用：%s") % name_trace)

    def gateway_validate(self, bundle, data):
        try:
            validate_converge_gateway(data)
        except exceptions.ConvergeMatchError as e:
            raise_validation_error(self, bundle, 'templates', 'data', e.message)


class PipelineInstanceResource(ModelResource):
    data = fields.ForeignKey(SnapshotResource, 'snapshot')
    exec_data = fields.ForeignKey(SnapshotResource, 'execution_snapshot')
    template = fields.ForeignKey(PipelineTemplateResource, 'template')

    pop_keys = ['is_deleted', 'edit_time', 'create_time', 'snapshot', 'template', 'is_finished', 'is_started',
                'finish_time', 'start_time', 'instance_id', 'execution_snapshot']

    class Meta:
        queryset = PipelineInstance.objects.filter(is_deleted=False)
        resource_name = 'instances'
        excludes = ['is_deleted', 'id']
        always_return_data = True
        detail_uri_name = 'instance_id'
        list_allowed_method = ['get', 'post']
        detail_allowed_methods = ['get', 'patch', 'post', 'delete']
        filtering = {
            'template': ALL_WITH_RELATIONS,
        }

        authorization = Authorization()
        serializer = PipelineSerializer()

    def dehydrate_data(self, bundle):
        return json.dumps(bundle.obj.snapshot.data)

    def dehydrate_exec_data(self, bundle):
        return json.dumps(bundle.obj.execution_snapshot.data)

    def hydrate(self, bundle):
        for key in self.pop_keys:
            if key in bundle.data:
                bundle.data.pop(key)

        return super(PipelineInstanceResource, self).hydrate(bundle)

    def alter_list_data_to_serialize(self, request, data):
        for bundle in data['objects']:
            bundle.data.pop('data')
            bundle.data.pop('exec_data')
            bundle.data.pop('description')
            bundle.data.pop('template')

        return data

    def alter_detail_data_to_serialize(self, request, data):
        bundle = data
        bundle.data.pop('template')

        return data

    def obj_create(self, bundle, **kwargs):
        template_id = bundle.data.get('template_id')
        try:
            template = PipelineTemplate.objects.get(template_id=template_id)
        except Exception:
            raise_validation_error(self, bundle,
                                   'instances', 'template_id', _(u"模板不存在"))

        exec_data = bundle.data.get('exec_data')
        try:
            exec_data = json.loads(exec_data)
        except Exception:
            raise_validation_error(self, bundle,
                                   'instances', 'exec_data', _(u"JSON 格式不合法"))

        # unfold subprocess
        unfold_subprocess(exec_data)
        instance_id = node_uniqid()
        exec_data['id'] = instance_id
        exec_snapshot, _ = Snapshot.objects.create_or_get_snapshot(exec_data)
        kwargs['template_id'] = template.id
        kwargs['instance_id'] = instance_id
        kwargs['snapshot_id'] = template.snapshot.id
        kwargs['execution_snapshot_id'] = exec_snapshot.id
        bundle.data.pop('exec_data')
        return super(PipelineInstanceResource, self).obj_create(bundle, **kwargs)

    def obj_update(self, bundle, skip_errors=False, **kwargs):
        exec_data = bundle.data['exec_data']
        try:
            data = json.loads(exec_data)
        except Exception:
            raise_validation_error(self, bundle,
                                   'instances', 'exec_data', _(u"JSON 格式不合法"))

        bundle.obj.execution_snapshot, _ = Snapshot.objects.create_or_get_snapshot(data)
        bundle.data.pop('exec_data')
        bundle.data.pop('data')
        return super(PipelineInstanceResource, self).obj_update(bundle, skip_errors=skip_errors, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        instance_id = kwargs['instance_id']
        PipelineInstance.objects.delete_model(instance_id)


class ComponentModelResource(ModelResource):
    class Meta:
        queryset = ComponentModel.objects.filter(status=1)
        resource_name = 'components'
        excludes = ['status', 'id']
        detail_uri_name = 'code'
        limit = 0

    def alter_list_data_to_serialize(self, request, data):
        for bundle in data['objects']:
            component = ComponentLibrary.get_component_class(bundle.data['code'])
            bundle.data['output'] = component.outputs_format()
            bundle.data['form'] = component.form

        return data

    def alter_detail_data_to_serialize(self, request, data):
        bundle = data
        component = ComponentLibrary.get_component_class(bundle.data['code'])
        bundle.data['output'] = component.outputs_format()
        bundle.data['form'] = component.form

        return data


class TemplateSchemeResource(ModelResource):
    template = fields.ForeignKey(PipelineTemplateResource, 'template')

    class Meta:
        queryset = TemplateScheme.objects.all()
        resource_name = 'schemes'

        filtering = {
            'template': ALL_WITH_RELATIONS,
        }
        authorization = Authorization()
        validation = FormValidation(form_class=forms.TemplateSchemeForm)

    def alter_list_data_to_serialize(self, request, data):
        for bundle in data['objects']:
            bundle.data.pop('data')

        return data

    def obj_create(self, bundle, **kwargs):
        template_id = bundle.data.get('template_id')
        try:
            template = PipelineTemplate.objects.get(template_id=template_id)
        except Exception:
            raise_validation_error(self, bundle,
                                   'schemes', 'template_id', _(u"模板不存在"))

        kwargs['template'] = template
        kwargs['unique_id'] = '%s-%s' % (template_id, bundle.data.get('name'))
        return super(TemplateSchemeResource, self).obj_create(bundle, **kwargs)
