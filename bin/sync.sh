#!/bin/bash

SCRIPT_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)

${SCRIPT_DIR}/sync_db.sh;
${SCRIPT_DIR}/sync_images.sh;