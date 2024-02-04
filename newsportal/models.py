from django.db import models
from newsportal.helpers import custom_slugify
from authentication_app.models import CustomUserModel
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os


class Category_Model(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_on_navbar = models.BooleanField(default=False)
    is_on_home = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Generate or update the slug based on the title
        base_slug = custom_slugify(self.title)
        self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Article_Model(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    content = models.TextField()
    description = models.TextField()
    category = models.ForeignKey(Category_Model, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image1 = models.ImageField(upload_to="articles/")
    image2 = models.ImageField(upload_to="articles/", null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Generate or update the slug based on the title
        base_slug = custom_slugify(self.title)
        self.slug = base_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


@receiver(post_delete, sender=Article_Model)
def delete_article_images(sender, instance, **kwargs):
    # Delete the article images after the article obj is completly deleted

    if instance.image1:
        delete_file(instance.image1.path)

    if instance.image2:
        delete_file(instance.image2.path)


def delete_file(filepath):
    """
    This Function deletes the image
    """
    if os.path.isfile(filepath):
        os.remove(filepath)
