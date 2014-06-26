from django.db import models

class GSE(models.Model):
    name = models.CharField(max_length=20)
    path = models.CharField(max_length=200)
    passed_gsms = models.TextField()
    failed_gsms = models.TextField()
    queued_gsms = models.TextField()
    running_gsms = models.TextField()

    passed = models.BooleanField()
    num_passed_gsms = models.PositiveSmallIntegerField()
    num_failed_gsms = models.PositiveSmallIntegerField()
    num_queued_gsms = models.PositiveSmallIntegerField()
    num_running_gsms = models.PositiveSmallIntegerField()

    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    updated = models.DateTimeField(auto_now=True, verbose_name='Updated')

    class Meta(object):
        verbose_name = 'GSE'
        verbose_name_plural = 'GSEs'

