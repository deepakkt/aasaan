from django.db import models
from django.contrib.auth.models import User
from smart_selects.db_fields import GroupedForeignKey
from contacts.models import Center, Zone, Contact


class AasaanUserCenter(models.Model):
    user = models.ForeignKey(User)
    center = GroupedForeignKey(Center, 'zone')

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