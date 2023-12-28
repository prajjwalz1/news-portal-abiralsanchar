from django.db import models
from django.utils.text import slugify
from newsportal.helpers import custom_slugify
from django.contrib.auth.models import User


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
        return self.name


class Article_Model(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True, editable=False)
    content = models.TextField()
    description = models.TextField()
    category = models.ForeignKey(Category_Model, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
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
