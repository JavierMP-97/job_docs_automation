from django.contrib.auth import get_user_model
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    experience = models.TextField(blank=True)
    education = models.TextField(blank=True)
    highlights = models.TextField(blank=True)
    hobbies = models.TextField(blank=True)
    languages = models.TextField(blank=True)
    other = models.TextField(blank=True)

class CoverLetter(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)