import os 
import json

import kronos
import paramiko
import yaml
import logging
logging.basicConfig(
    filename=os.path.join(os.path.dirname(__file__), 'cron_rsem_report.log'),
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO)

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
        logging.info(
            'not output returned from {0}@{1}, {2}, possible communication '
            'error with remote host'.format(C['username'], C['host'], C['cmd']))
        return
    data = json.loads(res[0])
    
    gsm_objs = []
    for path in data:
        for gse in data[path]:
            # _: ignore the value created variable
            gse_obj, _ = GSE.objects.get_or_create(name=gse)
            for species in data[path][gse]:
                # homo_sapiens => Homo sapiens
                species_name = species.replace('_', ' ').capitalize()
                species_obj, _ = Species.objects.get_or_create(name=species_name)
                for gsm in data[path][gse][species]:
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
                            logging.info('Updating {0}: {1} => {2}'.format(
                                gsm, gsm_obj.status, status))
                            for key, value in kwargs.iteritems():
                                setattr(gsm_obj, key, value)
                            gsm_obj.save()
                    except GSM.DoesNotExist:
                        logging.info('Creating {0}'.format(gsm))
                        gsm_obj = GSM(**kwargs)
                        gsm_objs.append(gsm_obj)
    GSM.objects.bulk_create(gsm_objs)

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
        else:
            # adapts to mannual changed, e.g. adding or removing GSMs after the
            # GSE is once passed
            if gse.passed == True:
                gse.passed = False
                gse.save()
