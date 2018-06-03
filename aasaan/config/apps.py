from os.path import join

from django.apps import AppConfig, apps
from django.conf import settings


class ConfigConfig(AppConfig):
    name = 'config'


def get_notify_models():
    _all_apps = apps.get_models()

    _notify_apps = []

    for _model in _all_apps:
        try:
            _notify_fields = _model.NotifyMeta.notify_fields
            _notify_apps.append(_model)
        except AttributeError:
            _notify_fields = []

    return tuple(_notify_apps)


def get_notify_models_namespaced():
    return [
        {repr(_x).split("'")[1]: _x} for _x in get_notify_models()
    ]


def get_notify_template_dict():
    _namespaced_models = [list(_x.items())[0] for _x 
                            in get_notify_models_namespaced()]
    _munge = lambda x: x.lower().replace(".", "_")                            


    return [
        {
            _munge(_x[0]) : 
            (_x[-1], _munge(_x[0]) + "_create.html",
                    _munge(_x[0]) + "_modify.html")
        }

        for _x in _namespaced_models
    ]


def get_notify_properties(model_class):
    # this is now just a wrapper function
    # with the logic moved to the class
    
    return model_class.get_notify_properties()