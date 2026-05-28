from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Movie(models.Model):
    title = models.CharField(max_length=500, db_index=True)
    year = models.IntegerField(null=True, blank=True)
    imdb_code = models.CharField(max_length=20, unique=True, db_index=True)
    imdb_votes = models.CharField(max_length=50)      # بدون کاما ذخیره شده (اسکریپ ما تمیزش کرد)
    imdb_rate = models.FloatField(db_index=True)
    download_links = models.JSONField(default=dict)
    poster_url = models.URLField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.year})"

    class Meta:
        ordering = ['-imdb_rate']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['title','-imdb_rate']),
        ]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, unique=True, db_index=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()