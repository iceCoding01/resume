from django.db import models
from django.utils.text import slugify
from django.conf import settings
import uuid

class Skill(models.Model):
    """Model representing a skill"""
    SKILL_CATEGORIES = (
        ('technical', 'Technical'),
        ('soft', 'Soft'),
        ('language', 'Language'),
        ('certification', 'Certification'),
        ('other', 'Other'),
    )
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True)
    category = models.CharField(max_length=50, choices=SKILL_CATEGORIES, default='technical')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class ProfileSkill(models.Model):
    """Model representing a skill associated with a profile"""
    profile = models.ForeignKey('Profile', on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency = models.PositiveSmallIntegerField(default=3, choices=(
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Expert'),
        (5, 'Master'),
    ))
    
    class Meta:
        unique_together = ('profile', 'skill')
        ordering = ['-proficiency', 'skill__name']
    
    def __str__(self):
        return f"{self.skill.name} ({self.get_proficiency_display()})"
