# main/signals.py

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import CustomUser

@receiver(post_save, sender=User)
def create_custom_user(sender, instance, created, **kwargs):
    if created:
        CustomUser.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_custom_user(sender, instance, **kwargs):
    # Check if CustomUser exists, create if it doesn't
    if not hasattr(instance, 'customuser'):
        CustomUser.objects.create(user=instance)
    else:
        instance.customuser.save()
