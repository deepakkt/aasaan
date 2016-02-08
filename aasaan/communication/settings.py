# Don't change tuple ordering! Used for setting model defaults!!
# Define additional communication types below
# they need to have corresponding dispatchers
COMMUNICATION_TYPES = (('EMail', 'EMail'),
                       ('SMS', 'SMS'),)

COMMUNICATION_STATUS = (('Pending', 'Pending'),
                        ('In Progress', 'In Progress'),
                        ('Complete', 'Complete'),
                        ('Error', 'Error'))

# Add other application specific contexts below
COMMUNICATION_CONTEXTS = (('Communication', 'Planned Communication'),
                          ('Transaction', 'Transactional Communication'))

# add dispatchers here. Define a new python module under communication
# say pushbullet.py or pushover.py. Include your logic there. Import the core function
# (added to dispatcher below) into api.py
communication_dispatcher = {'SMS': 'send_smscountry_sms',
                            'EMail': 'send_email'}

# sms defaults
sms_length_limit = 450  # allow upto 3 SMS'es as one SMS. More than that is unreliable
smscountry_api_url = "http://api.smscountry.com/SMSCwebservice_bulk.aspx"
