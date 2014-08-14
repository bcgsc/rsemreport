from django.shortcuts import render

from rsem_report.models import GSE

def get_gses_context(gses):
    """update and sort gses, and calculate total stats"""

    # total passed, running, queued, failed, none GSMs
    tp, tr, tq, tf, tn = [0] * 5
    for gse in gses:
        gse.passed_gsms = gse.gsm_set.filter(status='passed').order_by('name')
        gse.running_gsms = gse.gsm_set.filter(status='running').order_by('name')
        gse.queued_gsms = gse.gsm_set.filter(status='queued').order_by('name')
        gse.failed_gsms = gse.gsm_set.filter(status='failed').order_by('name')
        gse.none_gsms = gse.gsm_set.filter(status='none').order_by('name')

        gse.num_passed_gsms = gse.passed_gsms.count()
        tp += gse.num_passed_gsms
        gse.num_running_gsms = gse.running_gsms.count()
        tr += gse.num_running_gsms
        gse.num_queued_gsms = gse.queued_gsms.count()
        tq += gse.num_queued_gsms
        gse.num_failed_gsms = gse.failed_gsms.count()
        tf += gse.num_failed_gsms
        gse.num_none_gsms = gse.none_gsms.count()
        tn += gse.num_none_gsms

        gse.last_updated_gsm = max(gse.gsm_set.all(), key=lambda x: x.updated)

    context = dict(gses=sorted(gses, key=lambda x: x.name),
                   total_passed=tp,
                   total_running=tr,
                   total_queued=tq,
                   total_failed=tf,
                   total_none=tn)
    return context


def home(request):
    gses = GSE.objects.all()
    context = get_gses_context(gses)
    return render(request, 'rsem_report/progress_report.html', context)


def passed_GSMs(request):
    gses = GSE.objects.filter(passed=True)
    context = get_gses_context(gses)
    return render(request, 'rsem_report/progress_report.html', context)


def not_passed_GSMs(request):
    gses = GSE.objects.filter(passed=False)
    context = get_gses_context(gses)
    return render(request, 'rsem_report/progress_report.html', context)


def stats(request):
    gses = GSE.objects.all()
    context = get_gses_context(gses)
    for gse in gses:
        a, b, c, d, e = (gse.num_passed_gsms, gse.num_running_gsms,
                         gse.num_queued_gsms, gse.num_failed_gsms,
                         gse.num_none_gsms)
        gse.num_all_gsms = sum([a, b, c, d, e])
        gse.passed_gsms_percentage = float(a) / gse.num_all_gsms * 100
    gses = sorted(gses, key=lambda x: (x.passed_gsms_percentage, x.name))
    return render(request, 'rsem_report/stats.html', {'gses':context['gses']})

