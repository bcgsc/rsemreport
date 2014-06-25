from django.http import HttpResponse
from django.shortcuts import render

import utils as U
# Create your views here.
def home(request):
    res = U.sshexec('genesis.bcgsc.ca', 'zxue', '/home/zxue/zx_local/bin/python /extscratch/btl/zxue/rsem_pipeline/rsem_pipeline2/tools/gen_progress_report.py -d /extscratch/btl/zxue/rsem_pipeline/lele --json')
    return HttpResponse(res)
