flock -n $OPENSHIFT_REPO_DIR/createpack.lock -c python $OPENSHIFT_DEPLOYMENTS_DIR/current/repo/wsgi/myproject/manage.py createpack
