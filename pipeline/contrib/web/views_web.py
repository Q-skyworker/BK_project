# -*- coding: utf-8 -*-
from django.shortcuts import render


def home(request):
    """
    首页
    """
    return render(request, 'pipeline/home.html')


def template(request):
    """
    模板
    """
    return render(request, 'pipeline/template.html')


def instance(request):
    """
    实例
    """
    return render(request, 'pipeline/instance.html')


def newtask(request):
    """
    新建任務
    """
    return render(request, 'pipeline/newtask.html')
