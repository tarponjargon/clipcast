#!/bin/bash

# Ensure Task Spooler is configured with 5 slots
tsp -S 5

# Continue executing the container's main command
exec "$@"