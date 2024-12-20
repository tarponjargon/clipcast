#!/bin/bash

# alot of apps need to be synthesized in order to run the app
# so a start script is easiest to manage all the different parts

# 1. start docker compose
# 2. start webpack-dev-server, which proxies front end to back-end stack running on docker
# 3. start ngrok to expose the webpack-dev-server to the internet

# Ctrl-C stops everything

IMPORT_DATA=""
IMPORT_IMAGES=""
LOG="./devserver-startup.log"

rm ${LOG};
touch ${LOG};

# trap ctrl-c and call cleanup
trap cleanup SIGINT
function cleanup() {
  echo "Stopping server..."
  docker compose down;
  # kill ${WEBPACK_PID} 2>/dev/null;
  # kill ${NGROK_PID} 2>/dev/null;
}

function exit_with_error() {
  cleanup;
  exit 1
}

# trap errors
trap 'error ${LINENO}' ERR
error() {
  msg="Error on or near line $1 - check ${LOG} for more";
  echo ${msg};
  exit_with_error;
}

# watch log until all containers are completely
docker compose up --wait -d 2>&1 | tee -a ${LOG}

# install any new npm packages
echo "installing any new npm packages..."
npm install --legacy-peer-deps >> ${LOG} 2>&1

echo "Starting webpack-dev-server on ${DEVSERVER_HOST}, please wait..."
NODE_ENV=development WEB_HOST=${WEB_HOST} node_modules/.bin/webpack serve --mode development --config config/webpack.config.js

