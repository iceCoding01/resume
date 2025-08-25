
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
import uuid
import json

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    summary = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    profile_image = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    website = models.URLField(blank=True)
    
    def __str__(self):
        return self.full_name

class Education(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=100)
    degree = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
        
    def __str__(self):
        return f"{self.degree} at {self.institution}"

class Experience(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='experience')
    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    current = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
        
    def __str__(self):
        return f"{self.position} at {self.company}"

class Skill(models.Model):
    LEVEL_CHOICES = (
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    )
    
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=50)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='intermediate')
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name

class Project(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=100)
    description = models.TextField()
    technologies = models.CharField(max_length=200, blank=True)
    url = models.URLField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-end_date', '-start_date']
        
    def __str__(self):
        return self.title

class Certification(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='certifications')
    name = models.CharField(max_length=100)
    issuer = models.CharField(max_length=100)
    date_issued = models.DateField()
    expiration_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100, blank=True)
    credential_url = models.URLField(blank=True)
    
    class Meta:
        ordering = ['-date_issued']
        
    def __str__(self):
        return f"{self.name} by {self.issuer}"

class ResumeTemplate(models.Model):
    CATEGORY_CHOICES = (
        ('modern', 'Modern'),
        ('minimal', 'Minimal'),
        ('creative', 'Creative'),
        ('executive', 'Executive'),
    )
    
    name = models.CharField(max_length=50)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='modern')
    preview_image = models.URLField(blank=True)
    is_premium = models.BooleanField(default=False)
    html_template = models.CharField(max_length=100, default='classic.html')
    css_template = models.CharField(max_length=100, default='classic.css')
    
    def __str__(self):
        return self.name

class Resume(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes', null=True)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='user_resumes', null=True, blank=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    template = models.ForeignKey(ResumeTemplate, on_delete=models.SET_NULL, null=True, related_name='resumes')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    content = models.JSONField(default=dict, blank=True)
    custom_styles = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    share_token = models.CharField(max_length=100, blank=True, null=True, unique=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            unique_id = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_id}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class ResumeAnalytics(models.Model):
    ACTION_CHOICES = (
        ('viewed', 'Viewed'),
        ('pdf_generated', 'PDF Generated'),
        ('duplicated', 'Duplicated'),
        ('share_status_changed', 'Share Status Changed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='analytics_entries')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, default='viewed')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Resume Analytics'
    
    def set_metadata(self, data):
        self.metadata = json.dumps(data)
    
    def get_metadata(self):
        return json.loads(self.metadata)
    
    def log_view(self):
        """Log a view event for the resume"""
        self.action = 'viewed'
        self.save()
    
    def log_download(self):
        """Log a PDF download event for the resume"""
        self.action = 'pdf_generated'
        self.save()
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.resume.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"