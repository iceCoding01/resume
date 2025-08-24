from django.db import models
from .resume import Resume
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid

class ResumeView(models.Model):
    """Model to track resume views"""
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(max_length=500, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"View of {self.resume} at {self.timestamp}"

class ResumeEvent(models.Model):
    """Model to track events related to resumes"""
    EVENT_TYPES = (
        ('view', 'View'),
        ('download', 'Download'),
        ('share', 'Share'),
        ('apply', 'Apply')
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    # For tracking external actions (like clicks on job applications)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional metadata stored as JSON
    metadata = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return f"{self.event_type} event for {self.resume} at {self.timestamp}"
    
    class Meta:
        indexes = [
            models.Index(fields=['resume', 'event_type', 'timestamp']),
        ]
