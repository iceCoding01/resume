from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import os
import uuid
import logging

logger = logging.getLogger(__name__)

def generate_pdf(resume, context, download=True):
    """
    Generate a PDF from a resume using WeasyPrint
    
    Args:
        resume: The Resume model instance
        context: The context data for template rendering
        download: Boolean indicating if this is a download (attachment) or preview
    
    Returns:
        HttpResponse with PDF content
    """
    try:
        # Add metadata and tracking to context
        context.update({
            'generation_date': timezone.now(),
            'page_settings': {
                'size': 'letter',
                'margin': '1cm',
            }
        })
        
        # Get the template path based on the resume's template
        template_path = 'builder/pdf_templates/resume_pdf.html'
        if resume.template and hasattr(resume.template, 'html_template') and resume.template.html_template:
            template_path = resume.template.html_template
        
        # Render the template to a string
        html_string = render_to_string(template_path, context)
        
        # Create the HTTP response
        response = HttpResponse(content_type='application/pdf')
        
        # Set filename and disposition
        filename = f"{resume.slug}_{uuid.uuid4().hex[:8]}.pdf"
        if download:
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        # Collect stylesheets
        stylesheets = [
            CSS(string='@page { size: letter; margin: 1cm }'),
        ]
        
        # Add base PDF styles
        base_css_path = os.path.join(settings.STATIC_ROOT, 'css/pdf.css')
        if os.path.exists(base_css_path):
            stylesheets.append(CSS(filename=base_css_path))
        else:
            # Fallback to using the relative path
            stylesheets.append(CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/pdf.css')))
        
        # Add template-specific CSS if it exists
        if resume.template and hasattr(resume.template, 'css_file') and resume.template.css_file:
            template_css_path = os.path.join(settings.STATIC_ROOT, resume.template.css_file)
            if os.path.exists(template_css_path):
                stylesheets.append(CSS(filename=template_css_path))
            else:
                # Fallback to using the relative path
                stylesheets.append(CSS(filename=os.path.join(settings.BASE_DIR, 'static', resume.template.css_file)))
        
        # Add custom styles from the resume if they exist
        if resume.custom_styles:
            stylesheets.append(CSS(string=resume.custom_styles))
        
        # Generate PDF
        HTML(string=html_string).write_pdf(
            response,
            stylesheets=stylesheets
        )
        
        # Log the PDF generation for analytics
        if hasattr(resume, 'analytics'):
            if download:
                resume.analytics.log_download()
            else:
                resume.analytics.log_view()
        
        return response
        
    except Exception as e:
        logger.error(f"PDF generation error for resume {resume.id}: {str(e)}")
        # Return an error response or fallback to a simple PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="error-resume.pdf"'
        
        error_html = f"""
        <html>
            <body>
                <h1>Error Generating Resume</h1>
                <p>We encountered an error while generating your resume. Please try again later or contact support.</p>
                <p>Error reference: {uuid.uuid4().hex[:8]}</p>
            </body>
        </html>
        """
        
        HTML(string=error_html).write_pdf(response)
        return response

def save_pdf_to_file(resume, context, output_path):
    """
    Save a resume PDF to a file
    
    Args:
        resume: The Resume model instance
        context: The context data for template rendering
        output_path: Path where the PDF should be saved
    
    Returns:
        Path to the saved PDF file
    """
    try:
        # Get the template path based on the resume's template
        template_path = 'builder/pdf_templates/resume_pdf.html'
        if resume.template and hasattr(resume.template, 'html_template') and resume.template.html_template:
            template_path = resume.template.html_template
        
        # Add metadata to context
        context.update({
            'generation_date': timezone.now(),
            'page_settings': {
                'size': 'letter',
                'margin': '1cm',
            }
        })
        
        # Render the template to a string
        html_string = render_to_string(template_path, context)
        
        # Collect stylesheets
        stylesheets = [
            CSS(string='@page { size: letter; margin: 1cm }'),
        ]
        
        # Add base PDF styles
        base_css_path = os.path.join(settings.STATIC_ROOT, 'css/pdf.css')
        if os.path.exists(base_css_path):
            stylesheets.append(CSS(filename=base_css_path))
        else:
            # Fallback to using the relative path
            stylesheets.append(CSS(filename=os.path.join(settings.BASE_DIR, 'static/css/pdf.css')))
        
        # Add template-specific CSS if it exists
        if resume.template and hasattr(resume.template, 'css_file') and resume.template.css_file:
            template_css_path = os.path.join(settings.STATIC_ROOT, resume.template.css_file)
            if os.path.exists(template_css_path):
                stylesheets.append(CSS(filename=template_css_path))
            else:
                # Fallback to using the relative path
                stylesheets.append(CSS(filename=os.path.join(settings.BASE_DIR, 'static', resume.template.css_file)))
        
        # Add custom styles from the resume if they exist
        if resume.custom_styles:
            stylesheets.append(CSS(string=resume.custom_styles))
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate and save PDF
        HTML(string=html_string).write_pdf(
            output_path,
            stylesheets=stylesheets
        )
        
        return output_path
        
    except Exception as e:
        logger.error(f"PDF file save error for resume {resume.id}: {str(e)}")
        return None
