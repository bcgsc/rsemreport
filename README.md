# Description
`rsemreport` is a web app for monitoring the analysis progress of
[`rsempipeline`](https://github.com/bcgsc/rsem_pipeline "url to
rsem_pipeline")

# Install
    
    git clone git@github.com:bcgsc/rsemreport.git
    ROOT=${PWD}/rsemreport
    cd ${ROOT}
    virtualenv venv
    . venv/bin/activate
    pip install -r requirements.txt

    # create database
    python manage.py syncdb
	
# Configure the app

First you need to make sure the directory hierarchy on remote HPC and localhost
are the same

    cd /path/to/localhost/batchx/

This creates the same directory hierarchy as localhost, i.e in
remotehost/batchx, there will also be `rsem_output/GSE*/*/*`

    rsync -r -R rsem_output/GSE*/*/* username@hostname:/absolute/path/to/batchx/ --exclude="GSM[0-9]*/*"

Now, configure the cron job on localhost

    cd ${ROOT}/rsemreport

Send script to remote HPC for collecting progress data, you could just put it
in the home directory for simplicity

    rsync scripts_for_remote/collect_rsem_progress_data.py username@hostname:/home/username

Configure django cron job

    cp -v share/cron_config.yaml.template cron_config.yaml

Edit the yaml accordingly

    # do some editing

Install cron job

    cd ${ROOT}/rsemreport
    python manage.py installtasks

Check the installed cron job

    crontab -l

Make the task run for the first time to make sure it works, and collect
some initial data

    python manage.py runtask fetch_report_data

# Example for setting up cron jobs

    */10 * * * * /path/to/venv/bin/python /path/to/rsem_report/rsem_report/manage.py runtask fetch_report_data
    # the one below is created by python manage.py installtasks
    */10 * * * * /path/to/venv/bin/python /path/to/rsem_report/rsemreport/manage.py runtask fetch_report_data


# Start the server

    python manage.py runserver

or if you have installed [`foreman`](https://github.com/ddollar/foreman "url to
foreman") already,

    foreman start

Check logs

    # This logs the activity of the server
    less ${ROOT}/log/rsemreport.log

    # This logs the activity of the cron job
    less ${ROOT}/log/rsemreport_cron.log

# Screenshot

![screenshot](https://github.com/bcgsc/rsemreport/blob/master/rsemreport_screen_shot.jpg "screenshot")
