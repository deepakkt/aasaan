#!/usr/bin/python

import os
from datetime import date

def cleanup(rootpath, cutoffdays=8):
    file_list = os.listdir(rootpath)
    today = date.today()
    cutoff = date.fromordinal(today.toordinal() - cutoffdays)

    ordinal_map = [(date(*[int(x) for x in x.split('_')[-1].split('.')[0].split('-')])) for x in file_list]
    ordinal_map = zip(ordinal_map, file_list)
    delete_list = [x[-1] for x in ordinal_map if x[0] < cutoff]

    for eachdel in delete_list:
        each_file = os.path.join(rootpath, eachdel)
        os.remove(each_file)


rootpath="/home/deepak/dropbox/aasaan/database-backups"
cleanup(rootpath)
rootpath="/home/deepak/dropbox/aasaan/metabase"
cleanup(rootpath, cutoffdays=2)

