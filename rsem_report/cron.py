import os 
import json

import kronos
import paramiko
import yaml
import logging
logging.basicConfig(
    filename=os.path.expanduser('~/cron_rsem_report.log'),
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    level=logging.INFO)

from models import GSE

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
    data = json.loads(res[0])
    GSE_objs = []
    for gse in sorted(data.keys()):
        D = data[gse]
        passed = False if D['not_passed_gsms'] else True
        kwargs = dict(
            name=D['name'],
            path=', '.join(D['path']),
            passed_gsms=', '.join(D['passed_gsms']),
            not_passed_gsms=', '.join(D['not_passed_gsms']),
            
            passed=passed,
            num_passed_gsms=len(D['passed_gsms']),
            num_not_passed_gsms=len(D['not_passed_gsms']))
        try:
            gse_obj = GSE.objects.get(name=gse)
            if not gse_obj.passed:
                # need to do some update
                logging.info('Updating {0}'.format(gse))
                for key, value in kwargs.iteritems():
                    setattr(gse_obj, key, value)
                gse_obj.save()
        except GSE.DoesNotExist:
            logging.info('Creating {0}'.format(gse))
            gse_obj = GSE(**kwargs)
            GSE_objs.append(gse_obj)
    GSE.objects.bulk_create(GSE_objs)

