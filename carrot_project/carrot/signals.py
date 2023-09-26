from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
        User 모델이 저장될 때마다 UserProfile을 생성합니다.
    """
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
        User 모델이 저장될 때마다 UserProfile을 저장합니다.
    """
    instance.profile.save()
