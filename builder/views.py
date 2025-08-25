
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import json

from .models import (
    UserProfile, Education, Experience, Skill, Project, 
    Certification, ResumeTemplate, Resume, ResumeAnalytics
)

# Home page
def home(request):
    """Landing page with features and call to action"""
    templates = ResumeTemplate.objects.all()
    return render(request, 'builder/home.html', {'templates': templates})

# Dashboard
@login_required
def dashboard(request):
    """User dashboard with profile information and resumes"""
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
    )
    
    resumes = Resume.objects.filter(user_profile=profile)
    
    context = {
        'profile': profile,
        'resumes': resumes,
    }
    
    return render(request, 'builder/dashboard.html', context)

# Resume management
@login_required
def create_resume(request):
    """Create a new resume"""
    profile = get_object_or_404(UserProfile, user=request.user)
    template_id = request.GET.get('template')
    template = None
    
    if template_id:
        template = get_object_or_404(ResumeTemplate, id=template_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        template_id = request.POST.get('template')
        template = get_object_or_404(ResumeTemplate, id=template_id)
        
        resume = Resume.objects.create(
            user_profile=profile,
            title=title,
            template=template,
            status='draft'
        )
        
        # Create analytics record
        ResumeAnalytics.objects.create(resume=resume)
        
        messages.success(request, 'Resume created successfully')
        return redirect('edit_resume', slug=resume.slug)
    
    templates = ResumeTemplate.objects.all()
    return render(request, 'builder/create_resume.html', {
        'profile': profile,
        'templates': templates,
        'selected_template': template
    })

@login_required
def edit_resume(request, slug):
    """Edit an existing resume"""
    profile = get_object_or_404(UserProfile, user=request.user)
    resume = get_object_or_404(Resume, slug=slug, user_profile=profile)
    
    if request.method == 'POST':
        section = request.POST.get('section')
        action = request.POST.get('action')
        
        if section == 'resume':
            resume.title = request.POST.get('title')
            resume.status = request.POST.get('status', resume.status)
            
            if 'template' in request.POST:
                template_id = request.POST.get('template')
                resume.template = get_object_or_404(ResumeTemplate, id=template_id)
                
            resume.save()
            messages.success(request, 'Resume updated successfully')
            
        elif section == 'education':
            if action == 'add':
                Education.objects.create(
                    user_profile=profile,
                    institution=request.POST.get('institution'),
                    degree=request.POST.get('degree'),
                    field_of_study=request.POST.get('field_of_study', ''),
                    start_date=request.POST.get('start_date'),
                    end_date=request.POST.get('end_date') or None,
                    description=request.POST.get('description', '')
                )
                messages.success(request, 'Education added successfully')
            elif action == 'edit':
                education = get_object_or_404(Education, id=request.POST.get('id'), user_profile=profile)
                education.institution = request.POST.get('institution')
                education.degree = request.POST.get('degree')
                education.field_of_study = request.POST.get('field_of_study', '')
                education.start_date = request.POST.get('start_date')
                education.end_date = request.POST.get('end_date') or None
                education.description = request.POST.get('description', '')
                education.save()
                messages.success(request, 'Education updated successfully')
            
        elif section == 'experience':
            if action == 'add':
                current = 'current' in request.POST
                Experience.objects.create(
                    user_profile=profile,
                    company=request.POST.get('company'),
                    position=request.POST.get('position'),
                    location=request.POST.get('location', ''),
                    start_date=request.POST.get('start_date'),
                    end_date=request.POST.get('end_date') if not current else None,
                    current=current,
                    description=request.POST.get('description', '')
                )
                messages.success(request, 'Experience added successfully')
            elif action == 'edit':
                experience = get_object_or_404(Experience, id=request.POST.get('id'), user_profile=profile)
                current = 'current' in request.POST
                experience.company = request.POST.get('company')
                experience.position = request.POST.get('position')
                experience.location = request.POST.get('location', '')
                experience.start_date = request.POST.get('start_date')
                experience.end_date = request.POST.get('end_date') if not current else None
                experience.current = current
                experience.description = request.POST.get('description', '')
                experience.save()
                messages.success(request, 'Experience updated successfully')
            
        elif section == 'skill' and action == 'add':
            Skill.objects.create(
                user_profile=profile,
                name=request.POST.get('name'),
                level=request.POST.get('level', 'intermediate')
            )
            messages.success(request, 'Skill added successfully')
            
        elif section == 'project':
            if action == 'add':
                Project.objects.create(
                    user_profile=profile,
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    technologies=request.POST.get('technologies', ''),
                    url=request.POST.get('url', ''),
                    start_date=request.POST.get('start_date') or None,
                    end_date=request.POST.get('end_date') or None
                )
                messages.success(request, 'Project added successfully')
            elif action == 'edit':
                project = get_object_or_404(Project, id=request.POST.get('id'), user_profile=profile)
                project.title = request.POST.get('title')
                project.description = request.POST.get('description')
                project.technologies = request.POST.get('technologies', '')
                project.url = request.POST.get('url', '')
                project.start_date = request.POST.get('start_date') or None
                project.end_date = request.POST.get('end_date') or None
                project.save()
                messages.success(request, 'Project updated successfully')
            
        elif section == 'certification':
            if action == 'add':
                Certification.objects.create(
                    user_profile=profile,
                    name=request.POST.get('name'),
                    issuer=request.POST.get('issuer'),
                    date_issued=request.POST.get('date_issued'),
                    expiration_date=request.POST.get('expiration_date') or None,
                    credential_id=request.POST.get('credential_id', ''),
                    credential_url=request.POST.get('credential_url', '')
                )
                messages.success(request, 'Certification added successfully')
            elif action == 'edit':
                certification = get_object_or_404(Certification, id=request.POST.get('id'), user_profile=profile)
                certification.name = request.POST.get('name')
                certification.issuer = request.POST.get('issuer')
                certification.date_issued = request.POST.get('date_issued')
                certification.expiration_date = request.POST.get('expiration_date') or None
                certification.credential_id = request.POST.get('credential_id', '')
                certification.credential_url = request.POST.get('credential_url', '')
                certification.save()
                messages.success(request, 'Certification updated successfully')
            
        # Handle delete actions for all sections
        elif action == 'delete':
            item_id = request.POST.get('id')
            
            if section == 'education':
                education = get_object_or_404(Education, id=item_id, user_profile=profile)
                education.delete()
                messages.success(request, 'Education deleted successfully')
                
            elif section == 'experience':
                experience = get_object_or_404(Experience, id=item_id, user_profile=profile)
                experience.delete()
                messages.success(request, 'Experience deleted successfully')
                
            elif section == 'skill':
                skill = get_object_or_404(Skill, id=item_id, user_profile=profile)
                skill.delete()
                messages.success(request, 'Skill deleted successfully')
                
            elif section == 'project':
                project = get_object_or_404(Project, id=item_id, user_profile=profile)
                project.delete()
                messages.success(request, 'Project deleted successfully')
                
            elif section == 'certification':
                certification = get_object_or_404(Certification, id=item_id, user_profile=profile)
                certification.delete()
                messages.success(request, 'Certification deleted successfully')
        
        return redirect('edit_resume', slug=resume.slug)
    
    educations = Education.objects.filter(user_profile=profile)
    experiences = Experience.objects.filter(user_profile=profile)
    skills = Skill.objects.filter(user_profile=profile)
    projects = Project.objects.filter(user_profile=profile)
    certifications = Certification.objects.filter(user_profile=profile)
    templates = ResumeTemplate.objects.all()
    
    context = {
        'resume': resume,
        'profile': profile,
        'educations': educations,
        'experiences': experiences,
        'skills': skills,
        'projects': projects,
        'certifications': certifications,
        'templates': templates,
        'now': timezone.now().date(),  # For checking certification expiration
    }
    
    return render(request, 'builder/edit_resume.html', context)

@login_required
def edit_resume_new(request, slug):
    """Edit an existing resume with the new UI design"""
    profile = get_object_or_404(UserProfile, user=request.user)
    resume = get_object_or_404(Resume, slug=slug, user_profile=profile)
    
    if request.method == 'POST':
        section = request.POST.get('section')
        action = request.POST.get('action')
        
        if section == 'resume':
            resume.title = request.POST.get('title')
            resume.status = request.POST.get('status', resume.status)
            
            if 'template' in request.POST:
                template_id = request.POST.get('template')
                resume.template = get_object_or_404(ResumeTemplate, id=template_id)
                
            resume.save()
            messages.success(request, 'Resume updated successfully')
            
        elif section == 'education':
            if action == 'add':
                Education.objects.create(
                    user_profile=profile,
                    institution=request.POST.get('institution'),
                    degree=request.POST.get('degree'),
                    field_of_study=request.POST.get('field_of_study', ''),
                    start_date=request.POST.get('start_date'),
                    end_date=request.POST.get('end_date') or None,
                    description=request.POST.get('description', '')
                )
                messages.success(request, 'Education added successfully')
            elif action == 'edit':
                education = get_object_or_404(Education, id=request.POST.get('id'), user_profile=profile)
                education.institution = request.POST.get('institution')
                education.degree = request.POST.get('degree')
                education.field_of_study = request.POST.get('field_of_study', '')
                education.start_date = request.POST.get('start_date')
                education.end_date = request.POST.get('end_date') or None
                education.description = request.POST.get('description', '')
                education.save()
                messages.success(request, 'Education updated successfully')
            
        elif section == 'experience':
            if action == 'add':
                current = 'current' in request.POST
                Experience.objects.create(
                    user_profile=profile,
                    company=request.POST.get('company'),
                    position=request.POST.get('position'),
                    location=request.POST.get('location', ''),
                    start_date=request.POST.get('start_date'),
                    end_date=request.POST.get('end_date') if not current else None,
                    current=current,
                    description=request.POST.get('description', '')
                )
                messages.success(request, 'Experience added successfully')
            elif action == 'edit':
                experience = get_object_or_404(Experience, id=request.POST.get('id'), user_profile=profile)
                current = 'current' in request.POST
                experience.company = request.POST.get('company')
                experience.position = request.POST.get('position')
                experience.location = request.POST.get('location', '')
                experience.start_date = request.POST.get('start_date')
                experience.end_date = request.POST.get('end_date') if not current else None
                experience.current = current
                experience.description = request.POST.get('description', '')
                experience.save()
                messages.success(request, 'Experience updated successfully')
            
        elif section == 'skill' and action == 'add':
            Skill.objects.create(
                user_profile=profile,
                name=request.POST.get('name'),
                level=request.POST.get('level', 'intermediate')
            )
            messages.success(request, 'Skill added successfully')
            
        elif section == 'project':
            if action == 'add':
                Project.objects.create(
                    user_profile=profile,
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    technologies=request.POST.get('technologies', ''),
                    url=request.POST.get('url', ''),
                    start_date=request.POST.get('start_date') or None,
                    end_date=request.POST.get('end_date') or None
                )
                messages.success(request, 'Project added successfully')
            elif action == 'edit':
                project = get_object_or_404(Project, id=request.POST.get('id'), user_profile=profile)
                project.title = request.POST.get('title')
                project.description = request.POST.get('description')
                project.technologies = request.POST.get('technologies', '')
                project.url = request.POST.get('url', '')
                project.start_date = request.POST.get('start_date') or None
                project.end_date = request.POST.get('end_date') or None
                project.save()
                messages.success(request, 'Project updated successfully')
            
        elif section == 'certification':
            if action == 'add':
                Certification.objects.create(
                    user_profile=profile,
                    name=request.POST.get('name'),
                    issuer=request.POST.get('issuer'),
                    date_issued=request.POST.get('date_issued'),
                    expiration_date=request.POST.get('expiration_date') or None,
                    credential_id=request.POST.get('credential_id', ''),
                    credential_url=request.POST.get('credential_url', '')
                )
                messages.success(request, 'Certification added successfully')
            elif action == 'edit':
                certification = get_object_or_404(Certification, id=request.POST.get('id'), user_profile=profile)
                certification.name = request.POST.get('name')
                certification.issuer = request.POST.get('issuer')
                certification.date_issued = request.POST.get('date_issued')
                certification.expiration_date = request.POST.get('expiration_date') or None
                certification.credential_id = request.POST.get('credential_id', '')
                certification.credential_url = request.POST.get('credential_url', '')
                certification.save()
                messages.success(request, 'Certification updated successfully')
            
        # Handle delete actions for all sections
        elif action == 'delete':
            item_id = request.POST.get('id')
            
            if section == 'education':
                education = get_object_or_404(Education, id=item_id, user_profile=profile)
                education.delete()
                messages.success(request, 'Education deleted successfully')
                
            elif section == 'experience':
                experience = get_object_or_404(Experience, id=item_id, user_profile=profile)
                experience.delete()
                messages.success(request, 'Experience deleted successfully')
                
            elif section == 'skill':
                skill = get_object_or_404(Skill, id=item_id, user_profile=profile)
                skill.delete()
                messages.success(request, 'Skill deleted successfully')
                
            elif section == 'project':
                project = get_object_or_404(Project, id=item_id, user_profile=profile)
                project.delete()
                messages.success(request, 'Project deleted successfully')
                
            elif section == 'certification':
                certification = get_object_or_404(Certification, id=item_id, user_profile=profile)
                certification.delete()
                messages.success(request, 'Certification deleted successfully')
        
        return redirect('edit_resume_new', slug=resume.slug)
    
    educations = Education.objects.filter(user_profile=profile)
    experiences = Experience.objects.filter(user_profile=profile)
    skills = Skill.objects.filter(user_profile=profile)
    projects = Project.objects.filter(user_profile=profile)
    certifications = Certification.objects.filter(user_profile=profile)
    templates = ResumeTemplate.objects.all()
    
    context = {
        'resume': resume,
        'profile': profile,
        'educations': educations,
        'experiences': experiences,
        'skills': skills,
        'projects': projects,
        'certifications': certifications,
        'templates': templates,
        'now': timezone.now().date(),  # For checking certification expiration
    }
    
    return render(request, 'builder/new_edit_resume.html', context)

@login_required
def view_resume(request, slug):
    """View a resume"""
    resume = get_object_or_404(Resume, slug=slug)
    
    # If not the owner and resume is not published, deny access
    if resume.user_profile.user != request.user and resume.status != 'published':
        raise Http404("Resume not found")
    
    # Check if the user is the owner
    is_owner = resume.user_profile.user == request.user
    
    # Log view for analytics if not the owner
    if not is_owner:
        analytics, created = ResumeAnalytics.objects.get_or_create(resume=resume)
        analytics.log_view()
    
    profile = resume.user_profile
    educations = Education.objects.filter(user_profile=profile)
    experiences = Experience.objects.filter(user_profile=profile)
    skills = Skill.objects.filter(user_profile=profile)
    projects = Project.objects.filter(user_profile=profile)
    certifications = Certification.objects.filter(user_profile=profile)
    
    context = {
        'resume': resume,
        'profile': profile,
        'educations': educations,
        'experiences': experiences,
        'skills': skills,
        'projects': projects,
        'certifications': certifications,
        'is_owner': is_owner,
    }
    
    return render(request, 'builder/view_resume.html', context)

@login_required
def delete_resume(request, slug):
    """Delete a resume"""
    profile = get_object_or_404(UserProfile, user=request.user)
    resume = get_object_or_404(Resume, slug=slug, user_profile=profile)
    
    if request.method == 'POST':
        resume.delete()
        messages.success(request, 'Resume deleted successfully')
        return redirect('dashboard')
    
    return render(request, 'builder/delete_resume.html', {'resume': resume})

@login_required
def export_pdf(request, slug=None):
    """Export resume as PDF"""
    if slug:
        resume = get_object_or_404(Resume, slug=slug)
        
        # If not the owner and resume is not published, deny access
        if resume.user_profile.user != request.user and resume.status != 'published':
            raise Http404("Resume not found")
        
        # Log download for analytics
        if hasattr(resume, 'analytics'):
            resume.analytics.log_download()
        else:
            analytics = ResumeAnalytics.objects.create(resume=resume)
            analytics.log_download()
        
        # Generate PDF (we'll implement this later with WeasyPrint)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{resume.slug}.pdf"'
        
        # Placeholder
        response.write(b"PDF functionality coming soon!")
        
        return response
    
    return HttpResponse('No resume specified for PDF export.')

# Profile management
@login_required
def edit_profile(request):
    """Edit user profile"""
    profile = get_object_or_404(UserProfile, user=request.user)
    
    if request.method == 'POST':
        # Update profile fields
        profile.full_name = request.POST.get('full_name')
        profile.email = request.POST.get('email')
        profile.phone = request.POST.get('phone')
        profile.location = request.POST.get('location')
        profile.summary = request.POST.get('summary')
        profile.linkedin = request.POST.get('linkedin')
        profile.github = request.POST.get('github')
        profile.website = request.POST.get('website')
        profile.save()
        
        messages.success(request, 'Profile updated successfully')
        return redirect('dashboard')
    
    return render(request, 'builder/edit_profile.html', {'profile': profile})

def template_samples(request):
    """Display sample resume templates to users"""
    templates = ResumeTemplate.objects.all()
    
    # Group templates by category
    templates_by_category = {
        'modern': templates.filter(category='modern'),
        'minimal': templates.filter(category='minimal'),
        'creative': templates.filter(category='creative'),
        'executive': templates.filter(category='executive')
    }
    
    context = {
        'templates': templates,
        'templates_by_category': templates_by_category
    }
    
    return render(request, 'builder/samples.html', context)