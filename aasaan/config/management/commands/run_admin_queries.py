# -*- coding: utf-8 -*-

from datetime import datetime
import subprocess
import os

from django.core.management.base import BaseCommand
from django.conf import settings

from config.models import AdminQuery



class Command(BaseCommand):
    help = "Run one time queries staged by the admin"

    print("starting query admin")

    def handle(self, *args, **options):
        # set postgres password for non interactive execution
        os.environ['PGPASSWORD'] = settings.DB_PASSWORD

        for queries in AdminQuery.objects.filter(query_status='AP'):
            query = queries.query
            print(query)
            query_list = query.replace("\n", "").split(";")

            result = ""
            failed = False

            for each_query in query_list:
                result += each_query
                result += "\n"

                try:
                    query_result = subprocess.check_output(["psql", "-h", "localhost", "-U", "aasaan", "-c", each_query])
                    result += query_result.decode("utf-8")
                    result += "\n"
                except subprocess.CalledProcessError:
                    failed = True
                    result += "FAILED"
                    result += "\n"

            if failed:
                result = "THERE IS AT LEAST ONE FAILED QUERY. CHECK AND RESTAGE\n\n" + result
                queries.query_status = 'FA'
            else:
                queries.query_status = 'CO'

            queries.query_result = result
            print(result)
            queries.executed = datetime.now()
            queries.save()