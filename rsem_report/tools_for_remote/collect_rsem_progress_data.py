#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""example run of this script:
python collect_rsem_progress_data.py \
  -d rsem_output_dir [rsem_output_dir2, rsem_output_dir3, ...] \
  --qstat-cmd 'qstat -xml -u zxue'
"""

import os
import sys
import re
import json
import argparse

import subprocess

import xml.etree.ElementTree as xml

def get_qstat_data(qstat_cmd):
    proc = subprocess.Popen(qstat_cmd, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    # stdout: the raw_xml data wanted 
    return stdout

def get_jobs_from_qstat_data(qstat_cmd):
    """
    :param qstat_cmd: should be a list of strings
    """
    raw_xml = get_qstat_data(qstat_cmd)
    xml_data = xml.fromstring(raw_xml)
    queued_gsms, running_gsms = [], []
    # xpath: finding job_list recursively
    for job in xml_data.findall('.//job_list'):
        state = job.get('state')
        job_name = job.find('JB_name').text.strip()
        gsm_search = re.search('GSM\d+', job_name)
        if not gsm_search:
            continue
        gsm = gsm_search.group()
        if state == 'running':
            running_gsms.append(gsm)
        elif state == 'pending':
            queued_gsms.append(gsm)
    return running_gsms, queued_gsms


def collect_report_data_per_dir(
    dir_to_walk, running_gsms, queued_gsms, options):
    """
    :param running_gsms: running gsms determined from qstat output
    :param queued_gsms: queued_gsms determined from qstat output
    """
    res = {dir_to_walk: {}}
    for root, dirs, files in os.walk(os.path.abspath(dir_to_walk)):
        # gse_path: e.g. path/to/<GSExxxxxx>/<species>
        gse_path, gsm = os.path.split(root)
        species = os.path.basename(gse_path)
        gse = os.path.basename(os.path.dirname(gse_path))
        if re.search('GSM\d+$', gsm) and re.search('GSE\d+$', gse):
            if gse not in res[dir_to_walk]:
                res[dir_to_walk][gse] = {}
            dd = res[dir_to_walk][gse]

            if species not in dd:
                dd[species] = {}
            dd = res[dir_to_walk][gse][species]

            dd[gsm] = {}
            if not files:
                # if not files are found in the directory, it means the
                # analysis hasn't started yet, just the directory is
                # initialized
                dd[gsm].update(status='none')
            else:
                if options.flag_file in files:
                    # e.g. rsem.COMPLIETE exists, meaning passed
                    dd[gsm].update(status='passed')
                else:               # not passed
                    if gsm in queued_gsms:
                        dd[gsm].update(status='queued')
                    elif gsm in running_gsms:
                        dd[gsm].update(status='running')
                    else:
                        # if it's not in queue, and unfinished, assume it's a
                        # failed job
                        dd['failed_gsms'].update(status='failed')
    return res


def main():
    options = parse_args()
    qstat_cmd = options.qstat_cmd.split()
    running_gsms, queued_gsms = get_jobs_from_qstat_data(qstat_cmd)

    dirs_to_walk = options.dirs
    report_data = {}
    for dir_to_walk in dirs_to_walk:
        res = collect_report_data_per_dir(
            dir_to_walk, running_gsms, queued_gsms, options)
        report_data.update(res)

    # from pprint import pprint as pp
    # pp(report_data)
    sys.stdout.write(json.dumps(report_data))

def parse_args():
    parser = argparse.ArgumentParser(description='report progress of GSE analysis')
    parser.add_argument(
        '--qstat-cmd',
        help="shell command to fetch xml from qstat output, e.g. 'qstat -xml -u zxue'")
    parser.add_argument(
        '-d', '--dirs', required=True, nargs='+',
        help='''
The directory where GSE and GSM folders are located, must follow the hierachy like
rsem_output/
|-- GSExxxxx
|   `-- homo_sapiens
|       |-- GSMxxxxxxx
|       |-- GSMxxxxxxx
|-- GSExxxxx
|   `-- mus_musculus
|       |-- GSMxxxxxxx
'''),
    parser.add_argument(
        '--flag_file', default='rsem.COMPLETE',
        help='The name of the file whose existance signify compleition of a GSM analysis')
    options = parser.parse_args()
    return options
    

if __name__ == "__main__":
    main()
