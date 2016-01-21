#! /bin/bash
date   > $OPENSHIFT_DATA_DIR/last_date_cron_ran
flock -n $OPENSHIFT_DATA_DIR/createpack.lock -c python $OPENSHIFT_DEPLOYMENTS_DIR/current/repo/wsgi/myproject/manage.py createpack
