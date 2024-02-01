from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserModel(AbstractUser):
    profile_image = models.ImageField(upload_to="user_profile/", blank=True, null=True)
