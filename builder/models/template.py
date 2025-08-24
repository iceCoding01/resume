from django.db import models
from django.utils.text import slugify
from django.conf import settings
import uuid

class Template(models.Model):
    """Model representing a resume template"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField()
    preview_image = models.ImageField(upload_to='template_previews/')
    html_template = models.CharField(max_length=100)  # Path to template file
    css_file = models.CharField(max_length=100, blank=True, null=True)  # Optional custom CSS
    is_premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
