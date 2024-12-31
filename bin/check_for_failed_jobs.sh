#!/bin/bash

# Script to check completed tsp jobs and send notifications for failures

/usr/bin/tsp -l | awk '$2 == "finished"' | while read -r JOB_INFO; do
  JOB_ID=$(echo "$JOB_INFO" | awk '{print $1}')
  EXIT_STATUS=$(echo "$JOB_INFO" | awk '{print $4}')

  if [ "$EXIT_STATUS" -ne 0 ]; then
    /usr/bin/curl -d "Job $JOB_ID failed with exit status $EXIT_STATUS" ${ALERT_URL};
    #echo "Job $JOB_ID failed with exit status $EXIT_STATUS" | mail -s "Task Spooler Job Failed" your_email@example.com

  else
    echo "Job $JOB_ID completed successfully"
  fi

done