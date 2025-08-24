from builder.models import ResumeTemplate
from django.core.files import File
from pathlib import Path
import os
import shutil
import urllib.request
import tempfile

# Ensure templates directory exists in static folder
TEMPLATES_DIR = Path('builder/static/images/templates')
os.makedirs(TEMPLATES_DIR, exist_ok=True)

# Define professional template images
# In a real application, you'd have actual template preview images
# For now, we'll use placeholder images with better descriptions
templates = [
    {
        'name': 'Executive',
        'description': 'A premium template with elegant typography and structured layout. Perfect for executives, managers, and those in traditional industries like finance, law, or consulting.',
        'preview_url': 'https://resumegenius.com/wp-content/uploads/Executive-Resume-Template.png',
        'file_name': 'executive-template.png',
        'is_premium': True
    },
    {
        'name': 'Modern Professional',
        'description': 'Clean lines with a contemporary feel. This ATS-friendly template uses subtle design elements to organize your information professionally.',
        'preview_url': 'https://resumegenius.com/wp-content/uploads/Professional-Resume-Template.png',
        'file_name': 'modern-professional.png',
        'is_premium': False
    },
    {
        'name': 'Tech Innovator',
        'description': 'Designed specifically for IT professionals, developers, and tech industry candidates. Features sections for technical skills, projects, and coding proficiencies.',
        'preview_url': 'https://resumegenius.com/wp-content/uploads/IT-Resume-Template.png',
        'file_name': 'tech-innovator.png',
        'is_premium': False
    },
    {
        'name': 'Creative Director',
        'description': 'Bold, creative design for those in marketing, design, or creative fields. Includes space for portfolio highlights and visual elements.',
        'preview_url': 'https://resumegenius.com/wp-content/uploads/Creative-Resume-Template.png',
        'file_name': 'creative-director.png',
        'is_premium': True
    },
    {
        'name': 'Graduate',
        'description': 'Perfect for recent graduates or those with limited work experience. Emphasizes education, skills, and internships.',
        'preview_url': 'https://resumegenius.com/wp-content/uploads/College-Resume-Template.png',
        'file_name': 'graduate.png',
        'is_premium': False
    },
    {
        'name': 'Minimalist',
        'description': 'A streamlined, simple design that puts content first. Great for all industries and experience levels.',
        'preview_url': 'https://resumegenius.com/wp-content/uploads/Basic-Resume-Template.png',
        'file_name': 'minimalist.png',
        'is_premium': False
    }
]

def download_image(url, file_path):
    """Download an image from URL to the specified file path"""
    try:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            urllib.request.urlretrieve(url, temp_file.name)
            # Copy the temp file to the destination
            shutil.copy2(temp_file.name, file_path)
        return True
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return False

# Create each template if it doesn't already exist
created_count = 0
for template_data in templates:
    # Create the local file path
    file_path = TEMPLATES_DIR / template_data['file_name']
    
    # Download the image if it doesn't exist
    if not file_path.exists():
        success = download_image(template_data['preview_url'], file_path)
        if not success:
            # Use a default path if download fails
            template_data['preview_image'] = f"https://via.placeholder.com/400x550?text={template_data['name'].replace(' ', '+')}"
        else:
            # Use the local path
            template_data['preview_image'] = f"/static/images/templates/{template_data['file_name']}"
    else:
        # Use the local path
        template_data['preview_image'] = f"/static/images/templates/{template_data['file_name']}"
    
    # Create the template in the database
    template, created = ResumeTemplate.objects.get_or_create(
        name=template_data['name'],
        defaults={
            'description': template_data['description'],
            'preview_image': template_data['preview_image'],
            'is_premium': template_data['is_premium']
        }
    )
    
    # Update the description and preview image even if the template already exists
    if not created:
        template.description = template_data['description']
        template.preview_image = template_data['preview_image']
        template.save()
    
    created_count += 1

print(f"Added/updated {created_count} resume templates")
