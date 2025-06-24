from django.contrib.auth.models import User
from django.db import models

class Couple(models.Model):
    user1 = models.OneToOneField(User, related_name='couple_user1', on_delete=models.CASCADE)
    user2 = models.OneToOneField(User, related_name='couple_user2', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user1.username} & {self.user2.username}"

class Activity(models.Model):
    couple = models.ForeignKey(Couple, related_name='activities', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)
    last_suggested = models.DateField(null=True, blank=True)

    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('rejected', 'Rejected'),
        ('pool', 'Pool'),
        ('archived', 'Archived'),
        ('postponed', 'Postponed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

