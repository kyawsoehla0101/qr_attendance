# scanner/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    def __str__(self):
        return f"{self.user.id} - {self.user.get_full_name() or self.user.username}"

class QRLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    direction = models.CharField(max_length=10, choices=[('in', 'IN'), ('out', 'OUT')])
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.direction} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
