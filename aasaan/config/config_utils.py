from django.utils.text import slugify

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