from django.shortcuts import render

from rsem_report.models import GSE

def home(request):
    gses = GSE.objects.all()
    for gse in gses:
        gse.passed_gsms_as_list = gse.passed_gsms.split(', ')
        gse.not_passed_gsms_as_list = gse.not_passed_gsms.split(', ')
    return render(request, 'rsem_report/progress_report.html', {'gses':gses})

def passed_GSMs(request):
    gses = GSE.objects.filter(passed=True)
    for gse in gses:
        gse.passed_gsms_as_list = gse.passed_gsms.split(', ')
        gse.not_passed_gsms_as_list = gse.not_passed_gsms.split(', ')
    return render(request, 'rsem_report/progress_report.html', {'gses':gses})

    return 'NA'

def not_passed_GSMs(request):
    gses = GSE.objects.filter(passed=False)
    for gse in gses:
        gse.passed_gsms_as_list = gse.passed_gsms.split(', ')
        gse.not_passed_gsms_as_list = gse.not_passed_gsms.split(', ')
    return render(request, 'rsem_report/progress_report.html', {'gses':gses})

def stats(request):
    gses = GSE.objects.all()
    for gse in gses:
        a, b = gse.num_passed_gsms, gse.num_not_passed_gsms
        gse.passed_gsms_percentage = float(a)/(a + b) * 100
    gses = sorted(gses, key=lambda x: (x.passed_gsms_percentage, x.name))
    return render(request, 'rsem_report/stats.html', {'gses':gses})

