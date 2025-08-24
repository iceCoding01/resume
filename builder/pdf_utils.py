"""
PDF utility functions for resume generation
"""
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
import os
import uuid
import logging
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

def generate_pdf(resume, template=None, font='helvetica', color='blue'):
    """
    Generate a PDF from a resume using the specified template and styling
    
    Args:
        resume: Resume model instance
        template: ResumeTemplate model instance (or None to use resume.template)
        font: Font family to use (default: helvetica)
        color: Accent color to use (default: blue)
        
    Returns:
        tuple: (pdf_path, filename)
        
    Raises:
        Exception: If PDF generation fails
    """
    try:
        # Import here to avoid circular import
        from weasyprint import HTML, CSS
        from weasyprint.fonts import FontConfiguration
        
        # Use the resume's template if none provided
        if template is None:
            template = resume.template
            
        # Ensure the PDF directory exists
        pdf_dir = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        os.makedirs(pdf_dir, exist_ok=True)
        
        # Generate a unique filename
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        filename = f"resume-{resume.slug}-{timestamp}-{unique_id}.pdf"
        pdf_path = os.path.join(pdf_dir, filename)
        
        # Render the resume HTML
        html_content = render_to_string('resume_templates/export.html', {
            'resume': resume,
            'template': template,
            'font': font,
            'color': color,
            'export_mode': True,
            'generation_date': timezone.now(),
        })
        
        # Set up font configuration
        font_config = FontConfiguration()
        
        # Get CSS files
        base_css = os.path.join(settings.STATIC_ROOT, 'css/pdf.css')
        if not os.path.exists(base_css):
            # Fallback to using the relative path
            base_css = os.path.join(settings.BASE_DIR, 'static/css/pdf.css')
            
        # Template CSS
        template_css = None
        if template and hasattr(template, 'css_template') and template.css_template:
            template_css = os.path.join(settings.STATIC_ROOT, f'css/templates/{template.css_template}')
            if not os.path.exists(template_css):
                template_css = os.path.join(settings.BASE_DIR, f'static/css/templates/{template.css_template}')
                if not os.path.exists(template_css):
                    template_css = None
        
        # Collect stylesheets
        stylesheets = [
            CSS(string='@page { size: letter; margin: 1cm }', font_config=font_config),
            CSS(filename=base_css, font_config=font_config),
        ]
        
        # Add template CSS if it exists
        if template_css and os.path.exists(template_css):
            stylesheets.append(CSS(filename=template_css, font_config=font_config))
        
        # Additional styles based on font and color
        stylesheets.append(CSS(string=get_font_css(font), font_config=font_config))
        stylesheets.append(CSS(string=get_color_css(color), font_config=font_config))
        
        # Add custom styles from the resume if they exist
        if resume.custom_styles:
            stylesheets.append(CSS(string=resume.custom_styles, font_config=font_config))
        
        # Generate PDF
        html = HTML(string=html_content)
        html.write_pdf(pdf_path, stylesheets=stylesheets, font_config=font_config)
        
        logger.info(f"Generated PDF for resume {resume.slug}: {filename}")
        
        return pdf_path, filename
        
    except Exception as e:
        logger.error(f"PDF generation failed for resume {resume.slug}: {str(e)}")
        raise e


def generate_pdf_response(resume, template=None, font='helvetica', color='blue', download=True):
    """
    Generate a PDF response from a resume
    
    Args:
        resume: Resume model instance
        template: ResumeTemplate model instance (or None to use resume.template)
        font: Font family to use (default: helvetica)
        color: Accent color to use (default: blue)
        download: Boolean indicating if this is a download (attachment) or preview
    
    Returns:
        HttpResponse with PDF content
    """
    try:
        # Check if WeasyPrint is available
        from .weasyprint_utils import is_weasyprint_available, get_weasyprint_error_response
        
        if not is_weasyprint_available():
            return get_weasyprint_error_response()
        
        # Generate the PDF file
        pdf_path, filename = generate_pdf(resume, template, font, color)
        
        # Create the HTTP response
        with open(pdf_path, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        
        # Set filename and disposition
        if download:
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
        else:
            response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        # Track the download/view for analytics if applicable
        from .models import ResumeAnalytics
        ResumeAnalytics.objects.create(
            resume=resume,
            action='pdf_generated',
            metadata={
                'font': font,
                'color': color,
                'download': download,
            }
        )
        
        return response
        
    except Exception as e:
        # Handle errors
        error_message = handle_pdf_error(e)
        logger.error(f"PDF response generation error: {error_message}")
        
        # Import WeasyPrint error handler
        from .weasyprint_utils import get_weasyprint_error_response
        return get_weasyprint_error_response()


def handle_pdf_error(error):
    """
    Handle PDF generation errors with user-friendly messages
    
    Args:
        error: The exception that occurred
        
    Returns:
        str: User-friendly error message
    """
    error_str = str(error)
    
    if "Permission denied" in error_str:
        return "Could not save the PDF file due to permission issues. Please try again later."
    
    elif "Cannot connect to the host" in error_str:
        return "Could not connect to the PDF generation service. Please check your internet connection and try again."
    
    elif "Image not found" in error_str or "Failed to load image" in error_str:
        return "One or more images in your resume could not be loaded. Please ensure all image URLs are valid."
    
    elif "Missing required fonts" in error_str:
        return "Some required fonts are missing. Please try a different font."
    
    elif "Memory" in error_str:
        return "The system ran out of memory while generating your PDF. Please try simplifying your resume or try again later."
    
    elif "libgobject" in error_str or "GTK" in error_str:
        return "PDF generation requires GTK libraries. Please install GTK to enable PDF export."
    
    else:
        # Log the original error for debugging
        logger.error(f"Unhandled PDF generation error: {error_str}")
        return "An unexpected error occurred while generating your PDF. Please try again later."


def get_font_css(font):
    """
    Get CSS for the specified font
    
    Args:
        font: Font family name
        
    Returns:
        str: CSS rules for the font
    """
    font_map = {
        'helvetica': "'Helvetica Neue', Arial, sans-serif",
        'georgia': "Georgia, serif",
        'calibri': "Calibri, 'Segoe UI', sans-serif",
        'arial': "Arial, sans-serif",
        'times': "'Times New Roman', Times, serif",
    }
    
    font_family = font_map.get(font, font_map['helvetica'])
    
    return f"""
    body {{
        font-family: {font_family};
    }}
    """


def get_color_css(color):
    """
    Get CSS for the specified accent color
    
    Args:
        color: Color name
        
    Returns:
        str: CSS rules for the color
    """
    color_map = {
        'blue': '#3498db',
        'green': '#2ecc71',
        'red': '#e74c3c',
        'purple': '#9b59b6',
        'gray': '#34495e',
    }
    
    accent_color = color_map.get(color, color_map['blue'])
    
    return f"""
    h2, .section-title {{
        color: {accent_color};
    }}
    .skill-item {{
        background-color: {accent_color}20;
        border-left: 3px solid {accent_color};
    }}
    """


def get_pdf_download_url(filename):
    """
    Get the download URL for a PDF file
    
    Args:
        filename: PDF filename
        
    Returns:
        str: URL to download the PDF
    """
    return f"{settings.MEDIA_URL}pdfs/{filename}"
