from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
import pdb
import os

def _aasaan_sudo():
	import os
	return os.environ['AASAAN_SUDO']


env.use_ssh_config = True
env.hosts = [os.environ['AASAAN_HOST']]
env.user = os.environ['AASAAN_USER']
env.password = _aasaan_sudo()
env.key_filename = "~/.ssh/id_rsa"

def _code_dir():
    return "/home/deepak/django/aasaan"


def push_to_git():
    local("git push origin master")


@hosts(os.environ['AASAAN_SUDO'] + '@' + os.environ['AASAAN_HOST'])
def restart_aasaan():
    sudo('supervisorctl restart aasaan')


def deploy():    
    push_to_git()
    with cd(_code_dir()):
        run("git pull")
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/pip install -r requirements.txt")

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


def get_database_file(local_path="/tmp"):
    with cd("/home/deepak/dropbox/aasaan/database-backups"):
        dbfile = run("ls -1t | head -1")
        print(dbfile)
        get(dbfile, local_path=local_path)
    return os.path.join("/tmp", dbfile)


def sync_schedules():
    with cd(os.path.join(_code_dir(), 'aasaan')):
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py sync_sheets")
    
def sync_enrollments():
    with cd(os.path.join(_code_dir(), 'aasaan')):
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py sync_enrollments")

@hosts('ubuntu@aasaan-lxc')
def refresh_container_db():
    run("sudo -u postgres ./home/ubuntu/aasaan/deploy/load_aasaan_database_lxc.sh")



