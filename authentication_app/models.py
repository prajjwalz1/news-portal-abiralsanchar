from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserModel(AbstractUser):
    profile_image = models.ImageField(upload_to="user_profile/", blank=True, null=True)
    phone_number = models.DecimalField(
        max_digits=10, decimal_places=0, blank=True, null=True
    )
