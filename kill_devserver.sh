#!/bin/bash

PROC=$(ps -ef | awk '($9=="npm") {print $2}');

if [ -n "$PROC" ];
then
  echo "DEV SERVER PROCESS EXISTS: $PROC ... killing"
  sudo kill $PROC;
else
  echo "No dev server running"
fi

PROC=$(ps -ef | grep 'webpack' | grep -v grep | awk '{print $3}');

if [ -n "$PROC" ];
then
  echo "DEV SERVER PROCESS EXISTS: $PROC ... killing"
  sudo kill $PROC;
else
  echo "No dev server running"
fi
