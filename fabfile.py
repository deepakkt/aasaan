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


@hosts(os.environ['AASAAN_SUDO_USER'] + '@' + os.environ['AASAAN_HOST'])
def restart_aasaan():
    sudo('supervisorctl restart aasaan')
    sudo('supervisorctl restart aasaan-worker')


@hosts(os.environ['AASAAN_SUDO_USER'] + '@' + os.environ['AASAAN_HOST'])
def cert_renew_test():
    sudo('sudo certbot renew --dry-run')


@hosts(os.environ['AASAAN_SUDO_USER'] + '@' + os.environ['AASAAN_HOST'])
def cert_renew():
    sudo('sudo certbot renew')


def deploy_old():
    # deprecated. this is now centralized with the bash script
    local("git pull")
    push_to_git()
    with cd(_code_dir()):
        run("git pull")
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/pip install -r requirements.txt")

    with cd(os.path.join(_code_dir(), 'aasaan')):
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py migrate")
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py collectstatic --no-input")

    with cd(os.path.join(_code_dir(), 'deploy')):
        run("cp aasaan_sync_sheets ~/.virtualenvs/aasaan/bin")
        run("cp aasaan_hourly_cron ~/.virtualenvs/aasaan/bin")
        run("cp aasaan_worker_start ~/.virtualenvs/aasaan/bin")
        run("cp aasaan_backup_db ~/.virtualenvs/aasaan/bin")
        run("cp aasaan_backup_metabase ~/.virtualenvs/aasaan/bin")
        run("cp database_backup_clean.py ~/.virtualenvs/aasaan/bin")
        run("cp aasaan_deploy ~/.virtualenvs/aasaan/bin")
        run("chmod +x ~/.virtualenvs/aasaan/bin/aasaan_sync_sheets")
        run("chmod +x ~/.virtualenvs/aasaan/bin/aasaan_hourly_cron")
        run("chmod +x ~/.virtualenvs/aasaan/bin/aasaan_worker_start")
        run("chmod +x ~/.virtualenvs/aasaan/bin/aasaan_backup_db")
        run("chmod +x ~/.virtualenvs/aasaan/bin/aasaan_backup_metabase")
        run("chmod +x ~/.virtualenvs/aasaan/bin/aasaan_deploy")


def deploy():
    local("git pull")
    push_to_git()

    with cd("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin"):
        run("bash aasaan_deploy")


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
    run("sudo -u postgres /home/ubuntu/aasaan/deploy/load_aasaan_database_lxc.sh")


def refresh_dashboards():
    run("psql -f /home/deepak/django/aasaan/sql/refresh_irc_dashboard.sql")
    run("psql -f /home/deepak/django/aasaan/sql/statistics_dashboard.sql")


def backup_db():
    run("source /home/deepak/django/aasaan/.virtualenvs/aasaan/bin/aasaan_backup_db")

def joomla_history_sync():
    with cd(os.path.join(_code_dir(), 'aasaan')):
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py sync_joomla_counts 2017 1")
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py sync_joomla_counts 2017 2")
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py sync_joomla_counts 2017 3")
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py sync_joomla_counts 2017 4")
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py sync_joomla_counts 2017 5")
    

def sync_ors_counts():
    with cd(os.path.join(_code_dir(), 'aasaan')):
        run("/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/python manage.py sync_ors_counts")

