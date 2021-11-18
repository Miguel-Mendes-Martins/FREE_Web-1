from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Experiment(models.Model):
    name = models.CharField(_('Name'), max_length=64)
    slug = models.SlugField(_('Slug name'), max_length=64)
    description = models.TextField(_('Description'))
    config = models.JSONField(_('Configuration'), default=dict, blank=True)
    scientific_area = models.CharField(_('Scientific area'), max_length=64)
    lab_type = models.CharField(_('Lab type'), max_length=32)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Experiment')
        verbose_name_plural = _('Experiments')
        ordering = ['name']

class Apparatus(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.PROTECT, help_text=_('After setting/changing the experiment, press "%(button_name)s" to see the list of protocols.') % {'button_name' : _('Save and continue editing')})
    protocols = models.ManyToManyField('Protocol', blank=True)
    location = models.CharField(_('Location'), max_length=64)
    secret = models.CharField(_('Secret'), max_length=32)
    owner = models.CharField(_('Owner'), max_length=32)
    video_config = models.JSONField(_('Video configuration'), null=True, blank=True)

    def __str__(self):
        return _('%(experiment)s in %(location)s') % {'experiment': self.experiment.name, 'location': self.location}

    @property
    def current_status(self):
        try:
            return Status.objects.filter(apparatus=self).order_by('-time')[0].get_status_display()
        except:
            return Status(status='0').get_status_display()
            

    class Meta:
        verbose_name = _('Apparatus')
        verbose_name_plural = _('Apparatuses')
        ordering = ['location']

@receiver(post_save, sender=Apparatus)
def cleanup_protocols(sender, instance, created, **kwargs):
    for protocol in instance.protocols.all():
        if protocol.experiment != instance.experiment:
            instance.protocols.remove(protocol)

STATUS_CHOICES = (
    ('1', _('Online')),
    ('0', _('Offline')),
    ('R', _('Running')),
)

class Status(models.Model):
    apparatus = models.ForeignKey(Apparatus, on_delete=models.PROTECT)
    time = models.DateTimeField(_('Time'), auto_now=True)
    status = models.CharField(_('Status'), max_length=1, choices=STATUS_CHOICES)

    class Meta:
        verbose_name = _('Status')
        verbose_name_plural = _('Statuses')

class Protocol(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.PROTECT)
    name = models.CharField(max_length=64)
    config = models.JSONField(_('Configuration'), default=dict, blank=True) # JSON SCHEMA

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Protocol')
        verbose_name_plural = _('Protocols')
        ordering = ['name']

EXECUTION_STATUS_CHOICES = (
    ('N',_('New')),        # After clicking on start execution
    ('C',_('Configured')), # After creation by user
    ('Q',_('In queue')),   # After used approved that execution could be run 
    ('R',_('Running')),    # After requesting /nextexecution from RPI
    ('E',_('Error')),      # After request /execution/<int:id>/status change from RPI
    ('F',_('Finished')),   # After request /execution/<int:id>/status from RPI, or writing final result
    ('A',_('Aborted')),    # Not used now, in future triggered by user (needs endpoint)
    ('T',_('Timeout'))     # Not used now, possibly in future triggered by django
)

class Execution(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    apparatus = models.ForeignKey(Apparatus, on_delete=models.PROTECT)
    protocol = models.ForeignKey(Protocol, on_delete=models.PROTECT)
    config = models.JSONField(_('Configuration'), default=dict, blank=True)
    status = models.CharField(_('Status'), max_length=1, choices=EXECUTION_STATUS_CHOICES)
    queue_time = models.DateTimeField(null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return _('Execution of %(protocol)s') % {'protocol': str(self.protocol)}

    class Meta:
        verbose_name = _('Execution')
        verbose_name_plural = _('Executions')

    def save(self, *args, **kwargs):
        if self.status == 'Q' and not self.queue_time:
            self.queue_time = timezone.now()

        if self.status == 'R' and not self.start:
            self.start = timezone.now()

        if self.status in ['F','A','E'] and not self.end:
            self.end = timezone.now()
        
        super().save(*args, **kwargs)

RESULT_TYPES = {
    ('p', _('Partial')),
    ('f', _('Final')),
}

class Result(models.Model):
    execution = models.ForeignKey(Execution, on_delete=models.CASCADE)
    time = models.DateTimeField(_('Time'), auto_now=True)
    result_type = models.CharField(_('Result type'), max_length=1, choices=RESULT_TYPES)
    value = models.JSONField(_('Value'), default=dict, blank=True)

    def __str__(self):
        return _('Result of %(execution)s') % {'execution': str(self.execution) }

    class Meta:
        ordering = ['-id']
        verbose_name = _('Result')
        verbose_name_plural = _('Results')

USER_TYPES = (
    ('s', _('Student')),
    ('t', _('Teacher')),
    ('a', _('Administrator'))
)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name='profile')
    type = models.CharField(max_length=1, choices=USER_TYPES)

    def __str__(self):
        return _('Profile of ') + self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user = instance, type='s')
    instance.profile.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()