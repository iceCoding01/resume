"""
Utility functions for Django views to check if WeasyPrint dependencies are installed
"""
import os
import sys
import logging
from django.http import HttpResponse

logger = logging.getLogger(__name__)

def is_weasyprint_available():
    """Check if WeasyPrint is properly installed with all dependencies"""
    try:
        # Try to import WeasyPrint (this may fail on startup with missing GTK)
        # We'll wrap this import in a try/except block
        try:
            from weasyprint import HTML
            
            # On Windows, test if GTK dependencies are available
            if sys.platform.startswith('win'):
                try:
                    # Try to create a simple HTML object (will fail if GTK dependencies missing)
                    HTML(string="<html></html>")
                    return True
                except Exception as e:
                    logger.error(f"WeasyPrint GTK dependency error: {str(e)}")
                    return False
            
            # On other platforms, assume it's working if the import succeeded
            return True
            
        except ImportError as e:
            logger.error(f"WeasyPrint import error: {str(e)}")
            return False
        
    except Exception as e:
        logger.error(f"Unexpected error checking WeasyPrint: {str(e)}")
        return False

def get_weasyprint_error_response():
    """Return a user-friendly response for WeasyPrint errors"""
    html_content = """
    <html>
        <head>
            <title>PDF Generation Error</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
                h1 { color: #e74c3c; }
                .container { max-width: 800px; margin: 0 auto; }
                .error { background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0; }
                .info { background-color: #f8f9fa; border-left: 4px solid #17a2b8; padding: 15px; margin: 20px 0; }
                .steps { background-color: #f8f9fa; border-left: 4px solid #28a745; padding: 15px; margin: 20px 0; }
                code { background-color: #f1f1f1; padding: 2px 4px; border-radius: 4px; font-family: monospace; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>PDF Generation Error</h1>
                <p>We encountered an error while generating your PDF. This is likely due to missing GTK libraries on your system.</p>
                
                <div class="error">
                    <h3>Error Message:</h3>
                    <p>Cannot load library 'libgobject-2.0-0'. This is a common issue on Windows systems.</p>
                </div>
                
                <div class="info">
                    <h3>Technical Information:</h3>
                    <p>WeasyPrint requires GTK+3 libraries to function properly on Windows.</p>
                </div>
                
                <div class="steps">
                    <h3>Steps to Fix:</h3>
                    <ol>
                        <li>Download and install GTK+3 from <a href="https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases">https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases</a></li>
                        <li>Make sure to check the "Add to PATH" option during installation</li>
                        <li>Restart your computer after installation</li>
                        <li>Try exporting the PDF again</li>
                    </ol>
                </div>
                
                <p>For more information, please refer to the <a href="https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#windows">WeasyPrint documentation</a>.</p>
                
                <hr>
                <p>Note: PDF generation requires proper WeasyPrint and GTK installation. If you're a developer working on this application, make sure to install these dependencies.</p>
            </div>
        </body>
    </html>
    """
    
    return HttpResponse(html_content)
