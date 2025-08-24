
from django.contrib import admin
from .models import (
    UserProfile, Education, Experience, Skill, 
    Project, Certification, ResumeTemplate, Resume, ResumeAnalytics
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone')
    search_fields = ('full_name', 'email')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('institution', 'degree', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('institution', 'degree')

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('company', 'position', 'start_date', 'end_date', 'current')
    list_filter = ('start_date', 'end_date', 'current')
    search_fields = ('company', 'position')

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'level')
    list_filter = ('level',)
    search_fields = ('name',)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date')
    search_fields = ('title', 'technologies')

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('name', 'issuer', 'date_issued', 'expiration_date')
    list_filter = ('date_issued', 'expiration_date')
    search_fields = ('name', 'issuer')

@admin.register(ResumeTemplate)
class ResumeTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_premium')
    list_filter = ('is_premium',)
    search_fields = ('name', 'description')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_profile', 'template', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('title', 'user_profile__full_name')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(ResumeAnalytics)
class ResumeAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('resume', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('resume__title', 'action')
