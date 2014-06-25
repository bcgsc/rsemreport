from django.shortcuts import render

from rsem_report.models import GSE

def home(request):
    gses = GSE.objects.all()
    return render(request, 'rsem_report/progress_report.html', {'gses':gses})
