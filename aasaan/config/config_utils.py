from os.path import join as path_join
import subprocess
from datetime import datetime

from django.utils.text import slugify
from django.conf import settings

from .models import DatabaseRefresh


def getformatdateddmmyy(mydate):
    return "%02d/%02d/%d" % (mydate.day, mydate.month, mydate.year)


def getformatteddate(mydate):
    months = ['January', 'February', 'March', 'April', 'May',
    'June', 'July', 'August', 'September', 'October', 'November',
    'December']

    current_month = months[mydate.month - 1][:3]

    return "%02d-%s-%d" % (mydate.day, current_month, mydate.year)


def get_config_key(program, config, zone=None, prefix="ors-"):
    base = prefix + program
    if zone:
        base = base + " " + zone
    base = base + " " + config
    return slugify(base).upper().replace("-", "_")


def parse_config(configuration_dict, program_name, program_zone_name, config,
                 fallback_value="", raise_exception=True, prefix=""):
    config_value = configuration_dict.get(get_config_key(program_name,
                                                         config,
                                                         program_zone_name,
                                                         prefix))

    if not config_value:
        config_value = configuration_dict.get(get_config_key(program_name,
                                                             config,
                                                             prefix=prefix))

    if not config_value:
        if raise_exception:
            raise KeyError
        else:
            config_value = fallback_value

    return config_value


def refresh_database_backup(request_id=None, update_db_status=True):
    if not request_id:
        return None

    _bin_path = settings.BIN_ROOT
    _backup_script = path_join(_bin_path, "aasaan_backup_db")
    _docker_script = path_join(_bin_path, "aasaan_dropbox_sync")
    _status = "SU"

    try:
        _backup_result = subprocess.check_output([_backup_script])
    except subprocess.CalledProcessError:
        _status = "BF"
        
    try:
        _docker_result = subprocess.check_output([_docker_script])
    except subprocess.CalledProcessError:
        _status = "SF"

    if update_db_status:
        _db_object = DatabaseRefresh.objects.get(id=request_id)
        _db_object.refresh_status = _status
        _db_object.executed = datetime.now()
        _db_object.save()

         
        
    