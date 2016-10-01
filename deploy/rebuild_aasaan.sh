checkandabort()  {
	last_cmd_status=$1
	last_cmd_desc=$2
	if [[ ${last_cmd_status} != "0" ]]; then
		echo "Command not successful. Aborting. Please check the last executed command and attempt to fix error manually. Then try rerunning the script again."
		exit 1
	else
		echo "${last_cmd_desc} successful!"
	fi
	
}

blankline() {
	echo " "
}

if [[ "$EUID" -ne 0 ]]; then
	echo "Please run this script with sudo"
	exit 1
fi

rootpath=$1

echo "Proceeding with ${rootpath}"

if [[ -z "${rootpath}" ]]; then
	echo "Need root path of aasaan project to proceed"
	exit 1
fi


echo "Verifying if docker is installed..."

docker_exists=$(docker version | grep "Version" | wc -l)

if [[ ${docker_exists} = "2" ]]; then
 	echo "Docker detected, proceeding..."
else
	echo "Docker absent. Need to install docker to dockerify aasaan!"
	exit 1
fi

blankline

echo "Checking status of subnet for aasaan"

aasaan_subnet=$(docker network ls | grep aasaan_network | wc -l)

if [[ ${aasaan_subnet} = "1" ]]; then
	echo "Subnet exists. No action needed"
else
	echo "No subnet present. Attempting to create one"
	docker network create aasaan_network
	last_cmd_status=$?

	if [[ ${last_cmd_status} != "0" ]]; then
		echo "Unable to create subnet successfully. Aborting. Please inspect and attempt to create the subnet manually using 'docker network create aasaan_network'. If successful, you may rerun this script again"
		exit 1
	fi

	echo "Docker subnet creation successful"
fi

blankline

docker stop aasaan_nginx &> /dev/null
docker stop aasaan_redis &> /dev/null
docker stop aasaan_db &> /dev/null
docker stop aasaan &> /dev/null

aasaan_repo=${rootpath}/aasaan

if [[ -d ${aasaan_repo} ]]; then
	echo "Detected aasaan repo in ${aasaan_repo}"
else
	echo "No aasaan repo found. Clone the git repo into ${rootpath} or run with different root path. Aborting"
	exit 1
fi

blankline

aasaan_database=${rootpath}/aasaan-database
aasaan_static=${rootpath}/aasaan-static

echo "WARNING!! We will now remove the following folders"
echo "* ${aasaan_database}"
echo "* ${aasaan_static} "
echo "If you have contents from an earlier installation, you must be sure you don't want them. If you need them, stop now and back them up before proceeding. Hit 'yes' to proceed. Anything else will abort the script!"

read -p " ==> " script_proceed

if [[ ${script_proceed} = "yes" ]]; then
	echo "Proceeding to remove $aasaan_database and $aasaan_static"
else
	echo "You chose to abort."
	exit 0
fi

rm -rf $aasaan_database
rm -rf $aasaan_static
checkandabort "$?" "removal of folders"

echo "Removed $aasaan_database and $aasaan_static"
echo "Recreating $aasaan_database and $aasaan_static"

mkdir $aasaan_database
mkdir $aasaan_static
checkandabort "$?" "creation of folders"

echo "Successfully created $aasaan_database and $aasaan_static"

blankline

cd $aasaan_repo
pwd

blankline
blankline

echo "If this is the first time you are executing this build"
echo "it will take a loong time. Go for a walk, have lunch"
echo "and a cup of coffee. You can return back after evening darshan!"
echo "Ensure stable internet connection and do not abort process in the middle."
echo "Building images!"

blankline

echo "Building aasaan docker image"
docker build -t deepakkt/aasaan .
checkandabort "$?" "build of aasaan docker image"
blankline

echo "Building aasaan nginx image"
docker build -t deepakkt/aasaan_nginx -f $aasaan_repo/Dockerfile_nginx .
checkandabort "$?" "build of aasaan nginx image"
blankline

echo "Pulling docker image for redis"
docker pull redis:3.2.3-alpine
checkandabort "$?" "pull docker image for redis"
blankline

echo "Pulling docker image for postgres"
docker pull postgres:9.4.0
checkandabort "$?" "pull docker image for postgres"
blankline


echo "Removing existing containers, if any..."
docker rm aasaan_nginx &> /dev/null
docker rm aasaan_redis &> /dev/null
docker rm aasaan_db &> /dev/null
docker rm aasaan &> /dev/null
blankline

echo "Creating containers for aasaan"
echo "Creating redis container"
docker create --name aasaan_redis --network aasaan_network redis:3.2.3-alpine
checkandabort "$?" "creation of aasaan redis container"
blankline

echo "Creating nginx container"
docker create --name aasaan_nginx -v ${aasaan_static}:/var/www/aasaan --network=aasaan_network -p 80:80 deepakkt/aasaan_nginx
checkandabort "$?" "creation of aasaan nginx container"
blankline

echo "Creating postgres container"
docker create --name aasaan_db -e POSTGRES_USER=aasaan -e POSTGRES_PASSWORD=aasaan_admin -v ${aasaan_database}:/var/lib/postgresql/data --network=aasaan_network postgres:9.4.0
checkandabort "$?" "creation of postgres container"
blankline

echo "Finally, creating aasaan container"
docker create --name aasaan -v ${aasaan_static}:/var/www/aasaan --network=aasaan_network deepakkt/aasaan
checkandabort "$?" "creation of aasaan container"
blankline

docker ps --all | grep -i aasaan
blankline
echo "Woohoo!! All done and dusted! Everything seems to be successful!"
blankline
blankline

cp $aasaan_repo/deploy/aasaan_start /usr/local/bin
cp $aasaan_repo/deploy/aasaan_stop /usr/local/bin
chmod +x /usr/local/bin/aasaan*

blankline


echo "Now you may start aasaan with the command aasaan_start"
echo "Navigate to http://localhost. Login with user admin and password aasaan_admin"
echo "To stop the server issue aasaan_stop"
echo "Run this rebuild script if your source code changes. Otherwise aasaan_start"
echo "and aasaan_stop are sufficient to control the servers everytime"
echo "Enjoy your freshly minted aasaan instance! Good luck :)"
