from django.shortcuts import render
from django.core.cache import cache

from rsem_report import cron
from rsem_report.models import GSE

from utils import timeit


@timeit
def home(request):
    resp = cache.get('all_gses_response')
    if not resp:
        resp = cron.update_cache_all_gses()
    return resp

@timeit
def passed_GSEs(request):
    resp = cache.get('passed_gses_response')
    if not resp:
        resp = cron.update_cache_passed_gses()
    return resp


@timeit
def not_passed_GSEs(request):
    resp = cache.get('not_passed_gses_response')
    if not resp:
        resp = cron.update_cache_not_passed_gses()
    return resp


@timeit
def stats(request):
    resp = cache.get('stats_response')
    if not resp:
        resp = cron.update_cache_stats()
    return resp
