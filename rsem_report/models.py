from django.db import models

class GSE(models.Model):
    name = models.CharField(max_length=20)
    # if True, meaning all GSMs have been successfully analyzed 
    passed = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    updated = models.DateTimeField(auto_now=True, verbose_name='Updated')

    class Meta(object):
        verbose_name = 'GSE'
        verbose_name_plural = 'GSEs'


class Species(models.Model):
    name = models.CharField(max_length=20)


class GSM(models.Model):
    name = models.CharField(max_length=20)
    gse = models.ForeignKey('GSE')
    species = models.ForeignKey('Species')
    path = models.CharField(max_length=200)

    status = models.CharField(
        max_length=10,
        # passed: analysis finished successfully
        # failed: analysis didn't finish successfully
        # running: analysis hasn't finished yet
        # queued: analysis is found in the job scheduler queue
        # none: analysis hasn't started yet, e.g. empty directory detected
        choices=(('passed', 'passed'),
                 ('failed', 'failed'),
                 ('queued', 'queued'),
                 ('running', 'running'),
                 ('none', 'none')))

    created = models.DateTimeField(auto_now_add=True, verbose_name='Created')
    updated = models.DateTimeField(auto_now=True, verbose_name='Updated')

    class Meta(object):
        verbose_name = 'GSM'
        verbose_name_plural = 'GSMs'
