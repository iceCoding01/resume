from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from .profile import Profile
from .template import Template
import uuid

class Resume(models.Model):
    """Model representing a resume"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True)
    summary = models.TextField(blank=True)
    template = models.ForeignKey(Template, on_delete=models.SET_NULL, null=True, related_name='resumes')
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{str(self.id)[:8]}")
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('resume_detail', kwargs={'slug': self.slug})
    
    def __str__(self):
        return self.title

class ResumeSection(models.Model):
    """Model representing a section of a resume"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.title} - {self.resume.title}"

class ResumeItem(models.Model):
    """Model representing an item within a resume section"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(ResumeSection, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=100)
    subtitle = models.CharField(max_length=100, blank=True)
    date_range = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title
