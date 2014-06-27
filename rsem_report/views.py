from django.shortcuts import render

from rsem_report.models import GSE

def update_and_sort_gses(gses):
    for gse in gses:
        gse.passed_gsms_as_list = gse.passed_gsms.split(', ')
        gse.running_gsms_as_list = gse.running_gsms.split(', ')
        gse.queued_gsms_as_list = gse.queued_gsms.split(', ')
        gse.failed_gsms_as_list = gse.failed_gsms.split(', ')
    gses = sorted(gses, key=lambda x: x.name)
    return gses

def home(request):
    gses = GSE.objects.all()
    gses = update_and_sort_gses(gses)
    return render(request, 'rsem_report/progress_report.html', {'gses':gses})

def passed_GSMs(request):
    gses = GSE.objects.filter(passed=True)
    gses = update_and_sort_gses(gses)
    return render(request, 'rsem_report/progress_report.html', {'gses':gses})

def not_passed_GSMs(request):
    gses = GSE.objects.filter(passed=False)
    gses = update_and_sort_gses(gses)
    return render(request, 'rsem_report/progress_report.html', {'gses':gses})

def stats(request):
    gses = GSE.objects.all()
    for gse in gses:
        a, b, c, d = (gse.num_passed_gsms, gse.num_running_gsms,
                      gse.num_queued_gsms, gse.num_failed_gsms)
        gse.num_all_gsms = sum([a, b, c, d])
        gse.passed_gsms_percentage = float(a) / gse.num_all_gsms * 100
    gses = sorted(gses, key=lambda x: (x.passed_gsms_percentage, x.name))
    return render(request, 'rsem_report/stats.html', {'gses':gses})

