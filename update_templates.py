import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'resume.settings')
django.setup()

from builder.models import ResumeTemplate

def update_templates():
    """
    Update existing templates with categories if they don't have them
    and create some sample templates for each category if needed.
    """
    print("Updating template categories...")
    
    # Get all templates
    templates = ResumeTemplate.objects.all()
    
    print(f"Found {len(templates)} existing templates")
    
    # Ensure all templates have a category
    for template in templates:
        if not template.category:
            # Assign a default category based on the template name
            if 'modern' in template.name.lower():
                template.category = 'modern'
            elif 'minimal' in template.name.lower() or 'simple' in template.name.lower():
                template.category = 'minimal'
            elif 'creative' in template.name.lower() or 'design' in template.name.lower():
                template.category = 'creative'
            elif 'executive' in template.name.lower() or 'professional' in template.name.lower():
                template.category = 'executive'
            else:
                # Default to modern if we can't determine
                template.category = 'modern'
            
            template.save()
            print(f"Updated template '{template.name}' with category: {template.category}")
    
    # Check if we need to add more templates in other categories
    modern_count = ResumeTemplate.objects.filter(category='modern').count()
    minimal_count = ResumeTemplate.objects.filter(category='minimal').count()
    creative_count = ResumeTemplate.objects.filter(category='creative').count()
    executive_count = ResumeTemplate.objects.filter(category='executive').count()
    
    # Sample templates to add for different categories
    sample_templates = []
    
    # Add minimal templates if needed
    if minimal_count < 2:
        sample_templates.extend([
            {
                'name': 'Minimal Clean',
                'description': 'A minimalist design that focuses on content with clean typography.',
                'category': 'minimal',
                'is_premium': False,
                'html_template': 'minimal.html',
                'css_template': 'minimal.css',
            },
            {
                'name': 'Minimal Elegant',
                'description': 'An elegant, space-efficient design with subtle styling.',
                'category': 'minimal',
                'is_premium': False,
                'html_template': 'minimal_elegant.html',
                'css_template': 'minimal_elegant.css',
            },
        ])
    
    # Add creative templates if needed
    if creative_count < 2:
        sample_templates.extend([
            {
                'name': 'Creative Designer',
                'description': 'A bold, eye-catching resume for creative professionals.',
                'category': 'creative',
                'is_premium': True,
                'html_template': 'creative.html',
                'css_template': 'creative.css',
            },
            {
                'name': 'Creative Colorful',
                'description': 'A vibrant and colorful resume with unique layout elements.',
                'category': 'creative',
                'is_premium': True,
                'html_template': 'creative_colorful.html',
                'css_template': 'creative_colorful.css',
            },
        ])
    
    # Add executive templates if needed
    if executive_count < 2:
        sample_templates.extend([
            {
                'name': 'Executive Classic',
                'description': 'A traditional, professional resume for senior executives and managers.',
                'category': 'executive',
                'is_premium': True,
                'html_template': 'executive.html',
                'css_template': 'executive.css',
            },
            {
                'name': 'Executive Premium',
                'description': 'A premium resume design for C-level executives and senior professionals.',
                'category': 'executive',
                'is_premium': True,
                'html_template': 'executive_premium.html',
                'css_template': 'executive_premium.css',
            },
        ])
    
    # Create new templates
    for template_data in sample_templates:
        ResumeTemplate.objects.create(**template_data)
        print(f"Created template: {template_data['name']}")
    
    # Print summary of templates by category
    modern_count = ResumeTemplate.objects.filter(category='modern').count()
    minimal_count = ResumeTemplate.objects.filter(category='minimal').count()
    creative_count = ResumeTemplate.objects.filter(category='creative').count()
    executive_count = ResumeTemplate.objects.filter(category='executive').count()
    
    print("\nTemplate Summary:")
    print(f"Modern templates: {modern_count}")
    print(f"Minimal templates: {minimal_count}")
    print(f"Creative templates: {creative_count}")
    print(f"Executive templates: {executive_count}")
    print(f"Total templates: {ResumeTemplate.objects.count()}")

if __name__ == "__main__":
    update_templates()
    print("Template update completed!")
