#!/bin/bash

DUMPFILE=clipcast_mysqldump.queries
SCRIPT_DIR=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
HOME_DIR=$(dirname "${SCRIPT_DIR}") # parent of script dir

echo "exporting database remotely..."
ssh $REMOTE_HOST cgi-bin/mysqldump.cgi ;
echo "downloading data ..."
rsync -azv $REMOTE_HOST:$DUMPFILE ${HOME_DIR}/dev-sql/02.sql ;
sed -i 's/utf8mb4_0900_ai_ci/utf8mb4_unicode_ci/g' ${HOME_DIR}/dev-sql/02.sql ;
echo "deleting remote file..."
ssh $REMOTE_HOST "rm $DUMPFILE";
echo "backing up local db to  ${HOME_DIR}/tmp/dev-backup.sql "
mysqldump --no-tablespaces -u${MYSQL_USER} -h ${MYSQL_HOST} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} > ${HOME_DIR}/tmp/dev-backup.sql ;
echo "importing database locally..."
mysql -f -u${MYSQL_USER} -h ${MYSQL_HOST} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} < ${HOME_DIR}/dev-sql/02.sql ;
# echo "importing any migrations..."
# mysql -u${MYSQL_USER} -h ${MYSQL_HOST} -p${MYSQL_PASSWORD} ${MYSQL_DATABASE} < ${HOME_DIR}/migrations/initial.sql ;
#rm ${HOME_DIR}/$DUMPFILE ;
# ${SCRIPT_DIR}/updatecategories.pl;
echo "done."