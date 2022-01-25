from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime


class User(AbstractUser):
    pass


class Slot(models.Model):
    ''' user availability slots for schedule selection '''
    slot_interval = models.IntegerField()
    start_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_reserved = models.BooleanField(default=False)

    # end_time is calculated by adding interval to start_time
    @property
    def end_time(self):
        return self.start_time + datetime.timedelta(minutes=self.slot_interval)

    def __str__(self):
        return self.start_time.strftime('%d-%m-%Y %H:%M')


class Appointment(models.Model):
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_email = models.EmailField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username + ' - ' + self.slot.start_time.strftime('%d-%m-%Y %H:%M') + ' - ' + self.slot.end_time.strftime('%d-%m-%Y %H:%M')        