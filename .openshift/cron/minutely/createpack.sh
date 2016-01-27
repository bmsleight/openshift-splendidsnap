#! /bin/bash
nohup flock -n $OPENSHIFT_DATA_DIR/createpack.lock -c "python $OPENSHIFT_DEPLOYMENTS_DIR/current/repo/wsgi/myproject/manage.py createpack" > $OPENSHIFT_LOG_DIR/cron_logfile 2>&1 &
