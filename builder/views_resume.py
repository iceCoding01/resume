from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings

from .models import Resume, ResumeTemplate, ResumeAnalytics

import json
import os
import uuid
from datetime import datetime

# Import PDF utilities with lazy imports to avoid circular dependencies
def get_pdf_utils():
    from .pdf_utils import generate_pdf, handle_pdf_error
    return generate_pdf, handle_pdf_error

@login_required
def preview_resume(request, slug):
    """
    Display a preview of the resume with template selection options
    """
    resume = get_object_or_404(Resume, slug=slug, user=request.user)
    available_templates = ResumeTemplate.objects.all()
    
    # Check if it's an AJAX request for the preview content only
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        template_id = request.GET.get('template_id')
        font = request.GET.get('font', 'helvetica')
        color = request.GET.get('color', 'blue')
        
        if template_id:
            template = get_object_or_404(ResumeTemplate, id=template_id)
        else:
            template = resume.template
        
        # Render just the resume content
        html_content = render_to_string('resume_content.html', {
            'resume': resume,
            'template': template,
            'font': font,
            'color': color,
        })
        
        return HttpResponse(html_content)
    
    # Render the full preview page
    return render(request, 'preview_resume.html', {
        'resume': resume,
        'available_templates': available_templates,
    })


@login_required
def generate_resume_pdf(request, slug):
    """
    Generate a PDF of the resume and return the URL to download it
    Uses the WeasyPrint fallback mechanism
    """
    resume = get_object_or_404(Resume, slug=slug, user=request.user)
    
    # Get parameters
    template_id = request.GET.get('template_id')
    font = request.GET.get('font', 'helvetica')
    color = request.GET.get('color', 'blue')
    
    if template_id:
        template = get_object_or_404(ResumeTemplate, id=template_id)
    else:
        template = resume.template
    
    # Import the dependency checking functions
    from .weasyprint_utils import is_weasyprint_available
    
    # Check if WeasyPrint is available with dependencies
    if not is_weasyprint_available():
        # Return JSON error if WeasyPrint is not available
        return JsonResponse({
            'success': False,
            'error': 'PDF generation requires GTK libraries. Please install GTK from the link provided in the error page.',
            'html_fallback': True,
            'fallback_url': f"/resume/{resume.slug}/export-pdf/"
        })
    
    try:
        # WeasyPrint is available, proceed with PDF generation
        generate_pdf, handle_pdf_error = get_pdf_utils()
        pdf_path, filename = generate_pdf(
            resume=resume,
            template=template,
            font=font,
            color=color
        )
        
        # Create relative URL for the PDF
        media_url = settings.MEDIA_URL
        pdf_url = f"{media_url}pdfs/{filename}"
        
        # Record analytics
        ResumeAnalytics.objects.create(
            resume=resume,
            action='pdf_generated',
            metadata={
                'template': template.name,
                'font': font,
                'color': color,
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            }
        )
        
        return JsonResponse({
            'success': True,
            'pdf_url': pdf_url,
            'filename': filename
        })
        
    except Exception as e:
        # Handle errors
        generate_pdf, handle_pdf_error = get_pdf_utils()
        error_message = handle_pdf_error(e)
        return JsonResponse({
            'success': False,
            'error': error_message,
            'html_fallback': True,
            'fallback_url': f"/resume/{resume.slug}/export-pdf/"
        }, status=500)


@login_required
@require_POST
def duplicate_resume(request, slug):
    """
    Create a duplicate of an existing resume
    """
    original_resume = get_object_or_404(Resume, slug=slug, user=request.user)
    
    # Create a new resume with the same data
    new_resume = Resume.objects.create(
        user=request.user,
        title=f"Copy of {original_resume.title}",
        template=original_resume.template,
        content=original_resume.content,
        is_public=False  # Default to private for duplicates
    )
    
    # Record analytics
    ResumeAnalytics.objects.create(
        resume=new_resume,
        action='duplicated',
        metadata={
            'original_id': str(original_resume.id)
        }
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Resume duplicated successfully',
        'new_resume_id': new_resume.slug
    })


@login_required
def share_resume(request, slug):
    """
    Share a resume with a public link
    """
    resume = get_object_or_404(Resume, slug=slug, user=request.user)
    
    if request.method == 'POST':
        # Toggle public status
        resume.is_public = not resume.is_public
        
        # Generate a share token if making public
        if resume.is_public and not resume.share_token:
            resume.share_token = str(uuid.uuid4())
            
        resume.save()
        
        # Record analytics
        ResumeAnalytics.objects.create(
            resume=resume,
            action='share_status_changed',
            metadata={
                'is_public': resume.is_public
            }
        )
        
        return redirect('preview_resume', slug=resume.slug)
    
    return render(request, 'share_resume.html', {
        'resume': resume
    })


def public_resume_view(request, share_token):
    """
    Public view for shared resumes
    """
    resume = get_object_or_404(Resume, share_token=share_token, is_public=True)
    
    # Record view
    ResumeAnalytics.objects.create(
        resume=resume,
        action='viewed',
        metadata={
            'ip': get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'referrer': request.META.get('HTTP_REFERER', '')
        }
    )
    
    return render(request, 'public_resume.html', {
        'resume': resume
    })


@login_required
def resume_analytics(request, slug):
    """
    Display analytics for a resume
    """
    resume = get_object_or_404(Resume, slug=slug, user=request.user)
    
    # Get analytics data
    analytics = ResumeAnalytics.objects.filter(resume=resume).order_by('-created_at')
    
    # Calculate summary metrics
    view_count = analytics.filter(action='viewed').count()
    download_count = analytics.filter(action='pdf_generated').count()
    
    # Get view trend data (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_views = analytics.filter(
        action='viewed', 
        created_at__gte=thirty_days_ago
    )
    
    # Create trend data by day
    trend_data = {}
    for view in recent_views:
        date_str = view.created_at.strftime('%Y-%m-%d')
        if date_str in trend_data:
            trend_data[date_str] += 1
        else:
            trend_data[date_str] = 1
    
    # Format for chart JS
    trend_labels = list(trend_data.keys())
    trend_values = list(trend_data.values())
    
    return render(request, 'resume_analytics.html', {
        'resume': resume,
        'analytics': analytics[:50],  # Limit to 50 most recent
        'view_count': view_count,
        'download_count': download_count,
        'trend_labels': json.dumps(trend_labels),
        'trend_values': json.dumps(trend_values)
    })


@csrf_exempt
@require_POST
def resume_view_api(request):
    """
    API endpoint to record resume views from public pages
    """
    try:
        data = json.loads(request.body)
        share_token = data.get('share_token')
        referrer = data.get('referrer', '')
        
        if not share_token:
            return JsonResponse({'error': 'Share token is required'}, status=400)
        
        try:
            resume = Resume.objects.get(share_token=share_token, is_public=True)
        except Resume.DoesNotExist:
            return JsonResponse({'error': 'Resume not found'}, status=404)
        
        # Record analytics
        ResumeAnalytics.objects.create(
            resume=resume,
            action='viewed',
            metadata={
                'ip': get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'referrer': referrer
            }
        )
        
        return JsonResponse({'success': True})
    
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Helper function to get client IP
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
