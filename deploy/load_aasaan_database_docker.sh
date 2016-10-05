#!/bin/bash

if [[ "$EUID" -ne 0 ]]; then
	echo "Please run this script with sudo"
	exit 1
fi

echo "Verifying if postgres for aasaan is running"

aasaan_db_running=$(docker ps | grep "aasaan_db" | wc -l)

if [[ ${aasaan_db_running} = "1" ]]; then
 	echo "Aasaan postgres running..."
else
	echo "Please start aasaan for postgres"
	exit 1
fi

echo "Verifying if aasaan is running"

aasaan_running=$(docker ps | grep "deepakkt/aasaan" | wc -l)

if [[ ${aasaan_running} = "1" ]]; then
 	echo "Aasaan is running. Aasaan should be off when trying to load database"
    exit 1
else
	echo "Aasaan is not running. proceeding..."
fi

db_archive=$1

if [[ -z "${db_archive}" ]]; then
	echo "Specify full path for archive to load"
	exit 1
fi

echo "proceeding with archive ${db_archive}"

archive_extract_folder=$(mktemp -d)
archive_final_folder=$(mktemp -d)

tar -xf ${db_archive} -C ${archive_extract_folder}
find ${archive_extract_folder} -type f -exec mv -i {} ${archive_final_folder} \;
rm -rf ${archive_extract_folder}

archive_file=$(ls -1 ${archive_final_folder})

docker cp ${archive_final_folder}/${archive_file} aasaan_db:/tmp/
docker exec aasaan_db dropdb -U aasaan aasaan
docker exec aasaan_db createdb -U aasaan aasaan
docker exec aasaan_db psql -U aasaan -d aasaan -f /tmp/${archive_file}

rm -rf ${archive_final_folder}

docker exec aasaan_db rm /tmp/${archive_file}

echo "Everything appears to be successful."
echo "issue aasaan_stop and then aasaan_start"