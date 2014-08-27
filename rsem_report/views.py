from django.shortcuts import render
from django.core.cache import cache

from rsem_report import cron


def home(request):
    context = cache.get('all_gses')
    if not context:
        context = cron.update_cache_all_gses()
    return render(request, 'rsem_report/progress_report.html', context)


def passed_GSEs(request):
    context = cache.get('passed_gses')
    if not context:
        context = cron.update_cache_passed_gses()
    return render(request, 'rsem_report/progress_report.html', context)


def not_passed_GSEs(request):
    context = cache.get('not_passed_gses')
    if not context:
        context = cron.update_cache_not_passed_gses()
    return render(request, 'rsem_report/progress_report.html', context)


def stats(request):
    context = cache.get('all_gses')
    if not context:
        context = cron.update_cache_all_gses()
    gses = context['gses']
    for gse in gses:
        a, b, c, d, e = (gse.num_passed_gsms, gse.num_running_gsms,
                         gse.num_queued_gsms, gse.num_failed_gsms,
                         gse.num_none_gsms)
        gse.num_all_gsms = sum([a, b, c, d, e])
        gse.passed_gsms_percentage = float(a) / gse.num_all_gsms * 100
    gses = sorted(gses, key=lambda x: (x.passed_gsms_percentage, x.name))
    return render(request, 'rsem_report/stats.html', context)
