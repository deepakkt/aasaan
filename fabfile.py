from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
import pdb
import os

def _aasaan_sudo():
	import os
	return os.environ['AASAAN_SUDO']


env.use_ssh_config = True
env.hosts = ['aasaan.isha.in']
env.user = "aasaan"
env.password = _aasaan_sudo()
env.key_filename = "~/.ssh/id_rsa"

def _code_dir():
    return "/home/deepak/django/aasaan"


def push_to_git():
    local("git push origin master")


@hosts('deepak@aasaan.isha.in')
def restart_aasaan():
    sudo('supervisorctl restart aasaan')


def deploy():    
    push_to_git()
    with cd(_code_dir()):
        run("git pull")

    with cd(os.path.join(_code_dir(), 'aasaan')):
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py migrate")
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py collectstatic --no-input")

    with cd(os.path.join(_code_dir(), 'deploy')):
        run("cp aasaan_sync_sheets ~/.virtualenvs/aasaan/bin")
        run("cp aasaan_worker_start ~/.virtualenvs/aasaan/bin")
        run("cp aasaan_backup_db ~/.virtualenvs/aasaan/bin")
        run("chmod +x ~/.virtualenvs/aasaan/bin/aasaan_sync_sheets")
        run("chmod +x ~/.virtualenvs/aasaan/bin/aasaan_worker_start")
        run("chmod +x ~/.virtualenvs/aasaan/bin/aasaan_backup_db")
        

