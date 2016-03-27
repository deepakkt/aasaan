from django.db import models
from django.contrib.auth.models import User, Group

from contacts.models import Center, Zone, Contact

# Create your models here.
class AasaanUserCenter(models.Model):
    user = models.ForeignKey(User)
    center = models.ForeignKey(Center)

    def __str__(self):
        return "%s - %s" %(self.user.username, self.center)

class AasaanUserZone(models.Model):
    user = models.ForeignKey(User)
    zone = models.ForeignKey(Zone)

    def __str__(self):
        return "%s - %s" %(self.user.username, self.zone)


class AasaanUserContact(models.Model):
    user = models.ForeignKey(User)
    contact = models.OneToOneField(Contact)

    def __str__(self):
        return "%s - %s" % (self.user.username, self.contact.full_name)