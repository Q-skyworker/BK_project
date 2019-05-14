# -*- coding: utf-8 -*-

from common.mymako import render_mako_context
from gcloud.conf import settings


def home(request, biz_cc_id):
    context = {
        'biz_cc_id': biz_cc_id,
        'import_v1_flag': settings.IMPORT_V1_TEMPLATE_FLAG,
    }
    return render_mako_context(request, "/tasktmpl3/home.html", context)


def new(request, biz_cc_id):
    return render_mako_context(request, "/core/base_vue.html", {})


def edit(request, biz_cc_id):
    return render_mako_context(request, "/core/base_vue.html", {})


def clone(request, biz_cc_id):
    return render_mako_context(request, "/core/base_vue.html", {})


def newtask_selectnode(request, biz_cc_id):
    return render_mako_context(request, "/core/base_vue.html", {})


def newtask_paramfill(request, biz_cc_id):
    return render_mako_context(request, "/core/base_vue.html", {})

