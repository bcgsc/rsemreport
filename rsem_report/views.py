from django.shortcuts import render

from rsem_report.models import GSE

def home(request):
    gses = GSE.objects.all()
    for gse in gses:
        gse.passed_gsms_as_list = gse.passed_gsms.split(', ')
        gse.not_passed_gsms_as_list = gse.not_passed_gsms.split(', ')
    return render(request, 'rsem_report/progress_report.html', {'gses':gses})
