import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models.resume import Resume, ResumeSection, ResumeItem
from .models.profile import Profile
from .pdf_utils import generate_pdf

@login_required
@require_POST
def save_resume_section(request, resume_id):
    """
    AJAX endpoint to save a resume section
    """
    try:
        resume = Resume.objects.get(id=resume_id, profile__user=request.user)
        data = json.loads(request.body)
        
        section_id = data.get('section_id')
        section_data = data.get('section_data', {})
        
        if section_id:
            # Update existing section
            section = ResumeSection.objects.get(id=section_id, resume=resume)
            section.title = section_data.get('title', section.title)
            section.order = section_data.get('order', section.order)
            section.save()
        else:
            # Create new section
            section = ResumeSection.objects.create(
                resume=resume,
                title=section_data.get('title', 'New Section'),
                order=section_data.get('order', 0)
            )
        
        # Process items if provided
        if 'items' in section_data:
            for item_data in section_data['items']:
                item_id = item_data.get('id')
                if item_id:
                    # Update existing item
                    item = ResumeItem.objects.get(id=item_id, section=section)
                    item.title = item_data.get('title', item.title)
                    item.subtitle = item_data.get('subtitle', item.subtitle)
                    item.date_range = item_data.get('date_range', item.date_range)
                    item.description = item_data.get('description', item.description)
                    item.order = item_data.get('order', item.order)
                    item.save()
                else:
                    # Create new item
                    ResumeItem.objects.create(
                        section=section,
                        title=item_data.get('title', ''),
                        subtitle=item_data.get('subtitle', ''),
                        date_range=item_data.get('date_range', ''),
                        description=item_data.get('description', ''),
                        order=item_data.get('order', 0)
                    )
        
        return JsonResponse({'success': True, 'section_id': section.id})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def export_resume_pdf(request, resume_id):
    """
    Export a resume as PDF
    """
    try:
        resume = Resume.objects.get(id=resume_id, profile__user=request.user)
        
        # Prepare context for PDF generation
        context = {
            'resume': resume,
            'profile': resume.profile,
            'sections': resume.sections.all().order_by('order'),
        }
        
        # Generate PDF response
        return generate_pdf(resume, context)
        
    except Resume.DoesNotExist:
        return JsonResponse({'error': 'Resume not found'}, status=404)
