#!/bin/bash
DATE=`date +%Y%m%d_%H%M%S`

# The DB name must be the first and only argument
if [ $# -ne 1 ]; then
	echo "Usage: ./backupdb.sh <dbname>"
	exit 1
fi

mysqldump --add-drop-database --add-drop-table --routines --databases $1 > $1_$DATE.sql
