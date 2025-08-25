from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
import os
import uuid
import logging
from datetime import datetime
from django.conf import settings
from .models import Resume, ResumeAnalytics

# Configure logging
logger = logging.getLogger(__name__)

# Import the weasyprint availability checking function
from .weasyprint_utils import is_weasyprint_available, get_weasyprint_error_response

@login_required
def export_pdf_resume(request, slug):
    """Export resume as PDF with graceful fallback for Windows"""
    resume = get_object_or_404(Resume, slug=slug)
    
    # If not the owner and resume is not published, deny access
    if (hasattr(resume, 'user_profile') and resume.user_profile.user != request.user) and resume.status != 'published':
        raise Http404("Resume not found")
    
    # Log download for analytics
    if hasattr(resume, 'analytics'):
        resume.analytics.log_download()
    else:
        analytics = ResumeAnalytics.objects.create(resume=resume)
        analytics.log_download()
    
    # Check if WeasyPrint is available with all dependencies
    if not is_weasyprint_available():
        return get_weasyprint_error_response()
    
    try:
        # WeasyPrint is available, proceed with PDF generation
        from weasyprint import HTML, CSS
        
        # Render the resume HTML
        html_content = render_to_string('resume_templates/export.html', {
            'resume': resume,
            'template': resume.template,
            'export_mode': True,
        })
        
        # Generate PDF
        html = HTML(string=html_content)
        result = html.write_pdf()
        
        # Create HTTP response with PDF content
        response = HttpResponse(result, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{resume.slug}.pdf"'
        return response
        
    except Exception as e:
        # Log any errors that occur during PDF generation
        logger.error(f"PDF generation error: {str(e)}")
        return get_weasyprint_error_response()
