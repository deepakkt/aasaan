# -*- coding: utf-8 -*-

from datetime import datetime
import subprocess

from django.core.management.base import BaseCommand
from config.models import MasterDeploy



class Command(BaseCommand):
    help = "Make all latest commits in Master 'live'"

    print("starting deploy")

    def handle(self, *args, **options):
        for commit in MasterDeploy.objects.filter(deploy_status='ST'):
            print(commit.commit_title)

            try:
                commit_result = subprocess.check_output(["/home/deepak/django/aasaan/.virtualenvs/aasaan/bin/aasaan_deploy"])
            except subprocess.CalledProcessError:
                failed = True
                commit_result = "Failed for unknown reason. Please check your source changes"

            if failed:
                commit.deploy_status = 'FA'
            else:
                commit.deploy_status = 'CO'

            commit.deploy_result = commit_result
            print(commit.deploy_status)
            commit.executed = datetime.now()
            commit.save()