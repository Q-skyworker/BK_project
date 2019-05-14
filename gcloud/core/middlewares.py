# -*- coding: utf-8 -*-
import pytz
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from account.accounts import Account
from common.mymako import render_mako_context

from gcloud import exceptions
from gcloud.core import context_processors
from gcloud.core.utils import prepare_business


class GCloudPermissionMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        If a request path contains biz_cc_id parameter, check if current
        user has perm view_business or return http 403.
        """
        if getattr(view_func, 'login_exempt', False):
            return None
        biz_cc_id = view_kwargs.get('biz_cc_id')
        if biz_cc_id:
            try:
                business = prepare_business(request, cc_id=biz_cc_id)
            except exceptions.Unauthorized:
                # permission denied for target business (irregular request)
                return HttpResponse(status=406)
            except exceptions.Forbidden:
                # target business does not exist (irregular request)
                return HttpResponseForbidden()
            except exceptions.APIError as e:
                ctx = {
                    'system': e.system,
                    'api': e.api,
                    'message': e.message,
                }
                ctx.update(context_processors.get_constant_settings())
                return render_mako_context(request, '503.html', ctx)

            # set time_zone of business
            if business.time_zone:
                request.session['blueking_timezone'] = business.time_zone

            if not request.user.has_perm('view_business', business):
                return HttpResponseForbidden()


class UnauthorizedMiddleware(object):

    def process_response(self, request, response):
        if response.status_code in (403, 401):
            response = HttpResponse(
                content=_(u"您没有权限进行此操作"),
                status=405
            )
            if not request.is_ajax() and not getattr(request, 'FILES'):
                ctx = {}
                ctx.update(context_processors.get_constant_settings())
                return render_mako_context(request, '400.html', ctx)
        return response


class NotAcceptableMiddleware(object):

    def process_response(self, request, response):
        if response.status_code == 406:
            account = Account()
            response = account.redirect_login(request)
        return response


class TimezoneMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        tzname = request.session.get('blueking_timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
