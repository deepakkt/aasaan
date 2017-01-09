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
        return "%s - %s - %s - %d - %d" % (self.zone_name, self.program_name, self.program_window, self.participant_count, self.program_count)