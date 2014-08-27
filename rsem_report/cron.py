import os 
import json

import kronos
import paramiko
import yaml
import logging
logger = logging.getLogger(__name__)

from django.core.cache import cache
from django.shortcuts import render_to_response

from models import GSE, Species, GSM

with open(os.path.join(os.path.dirname(__file__), 'cron_config.yaml')) as inf:
    config = yaml.load(inf.read())

def sshexec(host, username, cmd, private_key_file='~/.ssh/id_rsa'):
    """
    :param private_key_file: could be ~/.ssh/id_dsa, as well
    """

    private_key_file = os.path.expanduser(private_key_file)
    rsa_key = paramiko.RSAKey.from_private_key_file(private_key_file)

    # This step will timeout after about 75 seconds if cannot proceed
    channel = paramiko.Transport((host, 22))
    channel.connect(username=username, pkey=rsa_key)
    session = channel.open_session()

    # if exec_command fails, None will be returned
    session.exec_command(cmd)

    # not sure what -1 does? learned from ssh.py
    output = session.makefile('rb', -1).readlines()
    channel.close()
    if output:
        return output

@kronos.register(config['fetch_report_data']['freq'])
def fetch_report_data():
    C = config['fetch_report_data']
    res = sshexec(C['host'], C['username'], C['cmd'])
    if not res:
        logger.error(res)
        logger.error(
            'not output returned from {0}@{1}, {2}, possible communication '
            'error with remote host'.format(C['username'], C['host'], C['cmd']))
        return
    data = json.loads(res[0])
    # logger.debug(data)          # too verbose
    
    changed = False             # to flag if anything has changed
    gsm_objs = []
    for path in sorted(data.keys()):
        for gse in sorted(data[path].keys()):
            # _: ignore the value created variable
            gse_obj, _ = GSE.objects.get_or_create(name=gse)
            for species in sorted(data[path][gse].keys()):
                # homo_sapiens => Homo sapiens
                species_name = species.replace('_', ' ').capitalize()
                species_obj, _ = Species.objects.get_or_create(name=species_name)
                for gsm in sorted(data[path][gse][species].keys()):
                    status = data[path][gse][species][gsm]['status']
                    kwargs = dict(
                        name=gsm,
                        gse=gse_obj,
                        species=species_obj,
                        path=os.path.join(path, gse, species, gsm),
                        status=status)
                    try:
                        gsm_obj = GSM.objects.get(name=gsm)
                        if gsm_obj.status != status:
                            # need to do some update
                            logger.info('Updating {0} {1}: {2} => {3}'.format(
                                gse, gsm, gsm_obj.status, status))
                            for key, value in kwargs.iteritems():
                                setattr(gsm_obj, key, value)
                            gsm_obj.save()
                            changed = True
                    except GSM.DoesNotExist:
                        logger.info('Creating {0}'.format(gsm))
                        gsm_obj = GSM(**kwargs)
                        gsm_objs.append(gsm_obj)
    if gsm_objs:
        GSM.objects.bulk_create(gsm_objs)
        changed = True

    # update GSEs based on passed
    gses = GSE.objects.all()
    for gse in gses:
        # passed_gsms = gse.gsm_set.filter(status='passed')
        running_gsms = gse.gsm_set.filter(status='running')
        queued_gsms = gse.gsm_set.filter(status='queued')
        failed_gsms = gse.gsm_set.filter(status='failed')
        none_gsms = gse.gsm_set.filter(status='none')

        if (running_gsms.count() == 0 and 
            queued_gsms.count() == 0 and
            failed_gsms.count() == 0 and
            none_gsms.count() == 0):
            if gse.passed == False:
                gse.passed = True
                gse.save()
                changed = True
        else:
            # adapts to mannual changed, e.g. adding or removing GSMs after the
            # GSE is once passed
            if gse.passed == True:
                gse.passed = False
                gse.save()
                changed = True
    if changed:
        logger.info('updating memcaches for all GSEs')
        update_cache_all_gses()
        logger.info('updating memcaches for passed GSEs')
        update_cache_passed_gses()
        logger.info('updating memcaches for not passed GSEs')
        update_cache_not_passed_gses()
        logger.info('updating memcaches for stats')
        update_cache_stats()
    else:
        logger.info('nothing changed')


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
    context.update(get_username_host_context())
    return context


def get_username_host_context():
    config_file = os.path.join(os.path.dirname(__file__), 'cron_config.yaml')
    with open(config_file) as inf:
        config = yaml.load(inf.read())
        C= config['fetch_report_data']
        return dict(username=C['username'], host=C['host'])


def get_num_for_header():
    return dict(num_all_gses=GSE.objects.all().count(),
                num_passed_gses=GSE.objects.filter(passed=True).count(),
                num_not_passed_gses = GSE.objects.filter(passed=False).count())


def update_cache_all_gses():
    # better check if the concent of cached content is outdated, but since it's
    # a cron job, speed won't be a big issue
    context = get_num_for_header()
    all_gses = GSE.objects.all()
    context.update(get_gses_context(all_gses))
    resp = render_to_response('rsem_report/progress_report.html', context)
    # None: cache forever until overwritten by cron.py fetch_report_data
    cache.set('all_gses_response', resp, None)
    return resp


def update_cache_passed_gses():
    context = get_num_for_header()
    passed_gses = GSE.objects.filter(passed=True)
    context.update(get_gses_context(passed_gses))
    resp = render_to_response('rsem_report/progress_report.html', context)
    cache.set('passed_gses_response', resp, None)
    return resp


def update_cache_not_passed_gses():
    context = get_num_for_header()
    not_passed_gses = GSE.objects.filter(passed=False)
    context.update(get_gses_context(not_passed_gses))
    resp = render_to_response('rsem_report/progress_report.html', context)
    cache.set('not_passed_gses_response', resp, None)
    return resp


def update_cache_stats():
    context = get_num_for_header()    
    all_gses = GSE.objects.all()
    context.update(get_gses_context(all_gses))
    gses = context['gses']
    for gse in gses:
        a, b, c, d, e = (gse.num_passed_gsms, gse.num_running_gsms,
                         gse.num_queued_gsms, gse.num_failed_gsms,
                         gse.num_none_gsms)
        gse.num_all_gsms = sum([a, b, c, d, e])
        gse.passed_gsms_percentage = float(a) / gse.num_all_gsms * 100
    gses = sorted(gses, key=lambda x: (x.passed_gsms_percentage, x.name))
    resp = render_to_response('rsem_report/stats.html', context)
    cache.set('stats_response', resp, None)
    return resp
