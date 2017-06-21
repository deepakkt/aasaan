#!/bin/bash

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

dropdb aasaan
createdb aasaan
psql -d aasaan -f ${archive_final_folder}/${archive_file}

rm -rf ${archive_final_folder}
rm ${db_archive}

echo "Everything appears to be successful."
