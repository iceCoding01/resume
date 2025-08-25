from builder.models import ResumeTemplate

# Map templates to categories
template_categories = {
    'Executive': 'executive',
    'Modern Professional': 'modern',
    'Tech Innovator': 'modern',
    'Creative Director': 'creative',
    'Graduate': 'minimal',
    'Minimalist': 'minimal',
}

updated_count = 0
for template_name, category in template_categories.items():
    templates = ResumeTemplate.objects.filter(name=template_name)
    
    for template in templates:
        template.category = category
        template.save()
        updated_count += 1
        print(f"Updated '{template.name}' with category '{category}'")

print(f"Updated {updated_count} templates with categories")
