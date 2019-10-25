#!/bin/sh

set -e

# Wait for the rabbitmq container
# See: https://docs.docker.com/compose/startup-order/
rabbit_host=${RABBITMQ_HOST:-localhost}
rabbit_port=${RABBITMQ_PORT:-5672}

until nc -vz $rabbit_host $rabbit_port; do
    >&2 echo "Waiting for RabbitMQ to be available..."
    sleep 1
done

>&2 echo "RabbitMQ is up."
