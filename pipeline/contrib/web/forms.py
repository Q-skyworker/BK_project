# -*- coding: utf-8 -*-
import ujson as json
from django import forms

from pipeline.models import PipelineTemplate, PipelineInstance, TemplateScheme
from pipeline.component_framework.models import ComponentModel
from pipeline.service import task_service

from django.utils.translation import ugettext_lazy as _


class PipelineTemplateForm(forms.ModelForm):
    class Meta:
        model = PipelineTemplate
        exclude = ['is_deleted', 'edit_time', 'create_time', 'snapshot', 'template_id']


class PipelineInstanceForm(forms.ModelForm):
    class Meta:
        model = PipelineInstance
        exclude = ['is_deleted', 'edit_time', 'create_time', 'snapshot', 'template', 'is_finished', 'is_started',
                   'finish_time', 'start_time', 'instance_id']


class TemplateSchemeForm(forms.ModelForm):
    class Meta:
        model = TemplateScheme
        exclude = ['edit_time']


class ActivityIDField(forms.CharField):
    def validate(self, value):
        super(ActivityIDField, self).validate(value)
        try:
            task_service.get_single_state(value)
        except:
            raise forms.ValidationError(_(u"无效的节点 ID"), code='invalid')


class InstanceIDField(forms.CharField):
    def validate(self, value):
        super(InstanceIDField, self).validate(value)
        try:
            PipelineInstance.objects.get(instance_id=value)
        except:
            raise forms.ValidationError(_(u"无效的实例 ID"), code='invalid')


class TemplateIDField(forms.CharField):
    def validate(self, value):
        super(TemplateIDField, self).validate(value)
        try:
            PipelineTemplate.objects.get(template_id=value)
        except:
            raise forms.ValidationError(_(u"无效的模板 ID"), code='invalid')


class InstanceActionForm(forms.Form):
    instance_id = InstanceIDField(max_length=32)


class NodeActionForm(forms.Form):
    node_id = ActivityIDField(max_length=32)


class ComponentCodeField(forms.CharField):
    def validate(self, value):
        super(ComponentCodeField, self).validate(value)
        try:
            ComponentModel.objects.get(code=value)
        except:
            raise forms.ValidationError(_(u"无效的组件代码"), code='invalid')


class JSONField(forms.CharField):
    def __init__(self, assert_type, *args, **kwargs):
        self.assert_type = assert_type
        super(JSONField, self).__init__(*args, **kwargs)

    def validate(self, value):
        super(JSONField, self).validate(value)
        try:
            l = json.loads(value)
            if self.assert_type and not isinstance(l, self.assert_type):
                raise forms.ValidationError(_(u"该字段的类型必须为 %s") % self.assert_type, code='invalid')
        except:
            raise forms.ValidationError(_(u"JSON 格式不合法"), code='invalid')


class ComponentFieldForm(forms.Form):
    component_code = ComponentCodeField()
    field = forms.CharField()


class RetryFieldsForm(forms.Form):
    act_id = ActivityIDField()
    component_code = ComponentCodeField()


class SubProcessFieldsForm(forms.Form):
    template_id = TemplateIDField()


class ActivityInputsForm(forms.Form):
    act_id = forms.CharField(max_length=32)
    instance_id = InstanceIDField()
    component_code = ComponentCodeField()
    subprocess_stack = JSONField(assert_type=list)

    def clean_subprocess_stack(self):
        return json.loads(self.cleaned_data['subprocess_stack'])


class InstanceConstantsModifyForm(forms.Form):
    instance_id = InstanceIDField()
    constants = JSONField(assert_type=dict)

    def clean_constants(self):
        return json.loads(self.cleaned_data['constants'])


class TemplateCloneForm(forms.Form):
    template_id = TemplateIDField()


class InstanceCloneForm(forms.Form):
    instance_id = InstanceIDField()
    creator = forms.CharField(max_length=32)


class ResetTimerForm(forms.Form):
    node_id = forms.CharField(max_length=32)
    inputs = JSONField(assert_type=dict)
