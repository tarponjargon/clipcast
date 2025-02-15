#!/bin/bash

# Ensure Task Spooler is configured with 5 slots
tsp -S 5

# start cron
cron -f &

# Continue executing the container's main command
exec "$@"
