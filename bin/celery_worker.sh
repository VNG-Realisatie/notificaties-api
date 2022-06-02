#!/bin/sh

set -e

# Figure out abspath of this script
SCRIPT=$(readlink -f "$0")
SCRIPTPATH=$(dirname "$SCRIPT")

LOGLEVEL=${CELERY_LOGLEVEL:-INFO}

# wait for required services
${SCRIPTPATH}/wait_for_db.sh
${SCRIPTPATH}/wait_for_rabbitmq.sh

echo "Starting celery worker"
celery --workdir src \
    --app nrc \
    worker \
    -l $LOGLEVEL
