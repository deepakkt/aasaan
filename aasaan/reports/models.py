from django.db import models

# Create your models here.
class IRCDashboardProgramCounts(models.Model):
    zone_name = models.CharField(max_length=100)
    program_name = models.CharField(max_length=100)
    program_window = models.CharField(max_length=10)
    program_count = models.IntegerField()

    class Meta:
        ordering = ['zone_name']


class IRCDashboardSectorCoordinators(models.Model):
    zone_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=100)
    centers = models.CharField(max_length=1500)

    class Meta:
        ordering = ['zone_name']


class IRCDashboardMissingRoles(models.Model):
    zone_name = models.CharField(max_length=100)
    center_name = models.CharField(max_length=100)
    role_level = models.CharField(max_length=25)
    available_roles = models.CharField(max_length=2000)
    missing_roles = models.CharField(max_length=2000)

    class Meta:
        ordering = ['zone_name', 'center_name']


class IRCDashboardZoneSummary(models.Model):
    zone_name = models.CharField(max_length=100)
    center_count = models.IntegerField()
    teacher_count = models.IntegerField()
    program_count = models.IntegerField()

    class Meta:
        ordering = ['zone_name']


class IRCDashboardRoleSummary(models.Model):
    zone_name = models.CharField(max_length=100)
    role_name = models.CharField(max_length=100)
    role_count = models.IntegerField()

    class Meta:
        ordering = ['zone_name', 'role_name']