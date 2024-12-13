#!/bin/bash

# didn't want to create a custom start script, but docker and webpack-dev-server + the custom hazel setup requires it.
# things have to orchestrated in a specific sequence that I couldn't perform with npm or docker

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
  kill ${WEBPACK_PID} 2>/dev/null;
  kill ${NGROK_PID} 2>/dev/null;
  exit 0;
}

# trap errors
trap 'error ${LINENO}' ERR
error() {
  msg="Error on or near line $1 - check ${LOG} for more";
  echo ${msg};
  cleanup;
}

# accept user input for conditional steps
read -r -p "Do you want to import fresh data? (takes 3-4 min) [y/N] " response
if [[ "$response" =~ ^(yes|y|Y)$ ]];
  then
    IMPORT_DATA="Y"
 fi

 read -r -p "Do you want to update images?  (takes 4-5 min, or 15-20 min if it's the first time) [y/N] " response
if [[ "$response" =~ ^(yes|y|Y)$ ]];
  then
    IMPORT_IMAGES="Y"
 fi

# watch log until all containers are completely
docker compose up --wait -d 2>&1 | tee -a ${LOG}

# if requested, sync data
if [[ "${IMPORT_DATA}" == "Y" ]];
  then
    sleep 5
    docker exec -i ${APP_HOST} sh -c 'exec /project/bin/sync_db.sh'
fi

# if requested, sync images
if [[ "${IMPORT_IMAGES}" == "Y" ]];
  then
    sleep 5
    docker exec -i ${APP_HOST} sh -c 'exec /project/bin/sync_images.sh'
fi

# install any new npm packages
echo "installing any new npm packages..."
npm install --legacy-peer-deps >> ${LOG} 2>&1

# run webpack-dev-server
echo "Starting webpack-dev-server on port ${DEVSERVER_PORT}, please wait..."
NODE_ENV=development WEB_HOST=${WEB_HOST} node_modules/.bin/webpack serve --mode development --config config/webpack.config.js | tee -a ${LOG} &
WEBPACK_PID=$!

echo "Starting ngrok on ${DEVSERVER_HOST}, please wait..."
ngrok http --url=${DEVSERVER_HOST} ${DEVSERVER_PORT} >> ${LOG} 2>&1
NGROK_PID=$!

wait $WEBPACK_PID $NGROK_PID