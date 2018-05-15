from django.db import models
from contacts.models import Zone
from django.contrib.auth.models import User


class Feedback(models.Model):
    title = models.CharField('Title', max_length=200)
    zone = models.ForeignKey(Zone, verbose_name='Zone', on_delete=models.CASCADE)
    STATUS_VALUES = (('SU', 'Submitted'),
                     ('AC', 'Acknowledged'),
                     ('IM', 'Implemented'),
                          )

    status = models.CharField(max_length=2, choices=STATUS_VALUES,
                                   default=STATUS_VALUES[0][0])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class FeedbackNotes(models.Model):
    feedback = models.ForeignKey(Feedback, on_delete=models.CASCADE)
    note = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return ""

    class Meta:
        ordering = ['-created']
        verbose_name = 'Feedback'