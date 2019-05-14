# coding=utf-8
"""
superuser command
"""
from django.core.cache import cache
from django.http import JsonResponse


def delete_cache_key(request, key):
    cache.delete(key)
    return JsonResponse({'result': True, 'data': 'success'})


def get_cache_key(request, key):
    data = cache.get(key)
    return JsonResponse({'result': True, 'data': data})
