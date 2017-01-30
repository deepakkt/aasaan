from django.db import models


class StatisticsProgramCounts(models.Model):
    zone_name = models.CharField(max_length=100)
    program_name = models.CharField(max_length=100)
    program_window = models.CharField(max_length=10)
    participant_count = models.IntegerField()
    program_count = models.IntegerField()

    class Meta:
        ordering = ['zone_name']

    def __str__(self):
        return "%s - %s - %s - %d - %d" % (
        self.zone_name, self.program_name, self.program_window, self.participant_count, self.program_count)


class OverseasEnrollement(models.Model):
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    center_name = models.CharField(max_length=100, null=True, blank=True)
    program_name = models.CharField(max_length=100, null=True, blank=True)
    no_of_day = models.IntegerField(null=True, blank=True)
    total_participants = models.IntegerField(null=True, blank=True)
    teacher_name = models.CharField(max_length=100, null=True, blank=True)
    co_teacher = models.CharField(max_length=150, null=True, blank=True)

    def __str__(self):
        return "%s - %s - %s" % (self.end_date, self.country, self.program_name)


class UyirNokkamEnrollement(models.Model):
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    zone = models.CharField(max_length=100, null=True, blank=True)
    no_of_classes = models.IntegerField(null=True, blank=True)
    no_of_participant = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "%s - %s" % (self.end_date, self.zone)


class TrainingStatistics(models.Model):
    month = models.DateField(null=True, blank=True)
    program_name = models.CharField(max_length=100, null=True, blank=True)
    no_of_full_time = models.IntegerField(null=True, blank=True)
    no_of_part_time = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return "%s - %s" % (self.month, self.program_name)

