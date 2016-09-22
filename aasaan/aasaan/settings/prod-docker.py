from .prod import *

# settings for running under docker
# use same as prod.py but override select parameters

# dockerified instances connect within a docker subnet
# connect to a named container called redis
RQ_QUEUES = {
    'default': {
        'HOST': 'aasaan_redis',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360,
    },
}


# same as above, allow 'nginx' as a valid host
ALLOWED_HOSTS += ['aasaan_nginx']
