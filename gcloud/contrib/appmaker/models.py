# coding=utf-8
import time

from django.db import models
from django.utils.translation import ugettext_lazy as _

from common.log import logger
from bk_api import (create_maker_app,
                    edit_maker_app,
                    del_maker_app)
from gcloud.conf import settings
from gcloud.tasktmpl3.models import TaskTemplate
from gcloud.core.models import Business
from gcloud.core.utils import (convert_readable_username,
                               name_handler,
                               time_now_str)


class AppMakerManager(models.Manager):

    def save_app_maker(self, biz_cc_id, template_id, app_params, app_id=None, fake=False):
        """
        @summary:
        @param biz_cc_id: 业务ID
        @param template_id: 模板ID
        @param app_params: App maker参数
        @param app_id: 为None则新建，否则编辑
        @param fake: 为True则不会真正调用API创建
        @return:
        """
        logger.info('save_app_maker param: %s' % app_params)
        biz = Business.objects.get(cc_id=biz_cc_id)
        try:
            task_template = TaskTemplate.objects.get(pk=template_id,
                                                     business__cc_id=biz_cc_id,
                                                     is_deleted=False)
        except TaskTemplate.DoesNotExist as e:
            return False, _(u"保存失败，引用的流程模板不存在！")

        # 处理可见范围，获取用户信息
        if not app_id:
            # create app_maker object
            kwargs = {
                'business': biz,
                'name': name_handler(app_params['app_name'], 20),
                'code': '',
                'desc': name_handler(app_params.get('app_desc', ''), 200),
                'logo_url': '',
                'link': app_params['app_link_prefix'],
                'creator': app_params['username'],
                'editor': app_params['username'],
                'task_template': task_template,
                'is_deleted': True,
            }
            if app_params.get('template_schema_id'):
                kwargs['template_schema_id'] = app_params['template_schema_id']
            app_maker_obj = AppMaker.objects.create(**kwargs)

            if fake:
                app_maker_obj.code = '%s%s' % (settings.APP_CODE, time_now_str())
                app_maker_obj.is_deleted = False
                app_maker_obj.save()
                return True, app_maker_obj.code

            # create app on blueking desk
            app_id = app_maker_obj.id
            app_link = '%s%s/newtask/%s/selectnode/?template_id=%s' % (
                app_params['app_link_prefix'],
                app_id,
                biz_cc_id,
                template_id)
            app_create_result = create_maker_app(
                app_params['username'],
                app_params['app_name'],
                app_link,
                app_params['username'],
                task_template.category,
                app_params.get('app_desc', ''),
            )
            if not app_create_result['result']:
                return None, _(u"创建轻应用失败：%s") % app_create_result['message']

            app_code = app_create_result['data']['app_code']
            app_logo_url = '%s/media/applogo/%s.png?v=%s' % (
                settings.BK_URL,
                app_code,
                time.time()
            )
            app_maker_obj.code = app_code
            app_maker_obj.link = app_link
            app_maker_obj.logo_url = app_logo_url
            app_maker_obj.is_deleted = False
            app_maker_obj.save()

            return True, app_code

        else:
            try:
                app_maker_obj = AppMaker.objects.get(
                    id=app_id,
                    business__cc_id=biz_cc_id,
                    task_template__id=template_id,
                    is_deleted=False
                )
            except AppMaker.DoesNotExist as e:
                return False, _(u"保存失败，当前操作的轻应用不存在或已删除！")

            app_code = app_maker_obj.code
            creator = app_maker_obj.creator

            if not fake:
                # edit app on blueking
                app_edit_result = edit_maker_app(
                    creator,
                    app_code,
                    app_params['app_name'],
                    '',
                    creator,
                    task_template.category,
                    app_params.get('app_desc', ''),
                )
                if not app_edit_result['result']:
                    return None, _(u"编辑轻应用失败：%s") % app_edit_result[
                        'message']

            # update app maker info
            app_logo_url = '%s/media/applogo/%s.png?v=%s' % (
                settings.BK_URL,
                app_code,
                time.time()
            )
            app_maker_obj.name = app_params['app_name']
            app_maker_obj.desc = app_params.get('app_desc', '')
            app_maker_obj.editor = app_params['username']
            if app_params.get('template_schema_id'):
                app_maker_obj.template_schema_id = app_params.get['template_schema_id']
            # cannot change bound task_template
            app_maker_obj.logo_url = app_logo_url
            app_maker_obj.save()

            return True, app_code

    def del_app_maker(self, biz_cc_id, app_id, company_code, fake=False):
        """
        @param app_id:
        @param biz_cc_id:
        @param company_code: 这里编辑
        @param fake:
        @return:
        """
        try:
            app_maker_obj = AppMaker.objects.get(
                id=app_id,
                business__cc_id=biz_cc_id,
                is_deleted=False
            )
        except AppMaker.DoesNotExist as e:
            return False, _(u"当前操作的轻应用不存在或已删除！")

        del_name = time_now_str()
        if not fake:
            # rename before delete to avoid name conflict when create a new app
            app_edit_result = edit_maker_app(
                app_maker_obj.creator,
                app_maker_obj.code,
                del_name[:20],
            )
            if not app_edit_result['result']:
                return False, _(u"删除失败：%s") % app_edit_result['message']

            # delete app on blueking desk
            app_del_result = del_maker_app(app_maker_obj.creator,
                                           app_maker_obj.code)
            if not app_del_result['result']:
                return False, _(u"删除失败：%s") % app_del_result['message']

        app_maker_obj.is_deleted = True
        app_maker_obj.name = del_name[:20]
        app_maker_obj.save()
        return True, app_maker_obj.code


class AppMaker(models.Model):
    """
    APP maker的基本信息
    """
    business = models.ForeignKey(Business, verbose_name=_(u"所属业务"))
    name = models.CharField(_(u"APP名称"), max_length=255)
    code = models.CharField(_(u"APP编码"), max_length=255)
    info = models.CharField(_(u"APP基本信息"), max_length=255, null=True)
    desc = models.CharField(_(u"APP描述信息"), max_length=255, null=True)
    logo_url = models.TextField(_(u"轻应用logo存放地址"), default='', blank=True)
    link = models.URLField(_(u"gcloud链接"), max_length=255)
    creator = models.CharField(_(u"创建人"), max_length=100)
    create_time = models.DateTimeField(_(u"创建时间"), auto_now_add=True)
    editor = models.CharField(_(u"编辑人"), max_length=100, null=True)
    edit_time = models.DateTimeField(_(u"编辑时间"), auto_now=True, null=True)
    task_template = models.ForeignKey(TaskTemplate, verbose_name=_(u"关联模板"))
    template_schema_id = models.CharField(_(u"执行方案"), max_length=100, blank=True)
    is_deleted = models.BooleanField(_(u"是否删除"), default=False)

    objects = AppMakerManager()

    @property
    def creator_name(self):
        return convert_readable_username(self.creator)

    @property
    def editor_name(self):
        return convert_readable_username(self.editor)

    @property
    def task_template_name(self):
        return self.task_template.name

    @property
    def category(self):
        return self.task_template.category

    def __unicode__(self):
        return u'%s_%s' % (self.business, self.name)

    class Meta:
        verbose_name = u"轻应用 AppMaker"
        verbose_name_plural = u"轻应用 AppMaker"
        ordering = ['-id']
