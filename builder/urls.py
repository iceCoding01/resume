from django.urls import path
from . import views, views_resume
from .pdf_export import export_pdf_resume

urlpatterns = [
    # Main views
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('templates/samples/', views.template_samples, name='template_samples'),
    path('templates/<int:template_id>/customize/', views.customize_template, name='customize_template'),
    
    # Resume CRUD operations
    path('resume/create/', views.create_resume, name='create_resume'),
    path('resume/<slug:slug>/edit/', views.edit_resume, name='edit_resume'),
    path('resume/<slug:slug>/edit-new/', views.edit_resume_new, name='edit_resume_new'),
    path('resume/<slug:slug>/view/', views.view_resume, name='view_resume'),
    path('resume/<slug:slug>/delete/', views.delete_resume, name='delete_resume'),
    
    # Resume preview and PDF
    path('resume/<slug:slug>/preview/', views_resume.preview_resume, name='preview_resume'),
    path('resume/<slug:slug>/generate-pdf/', views_resume.generate_resume_pdf, name='generate_resume_pdf'),
    path('resume/<slug:slug>/duplicate/', views_resume.duplicate_resume, name='duplicate_resume'),
    path('resume/<slug:slug>/export-pdf/', export_pdf_resume, name='export_pdf_resume'),
    path('export-pdf/', views.export_pdf, name='export_pdf'),
    
    # Sharing and analytics
    path('resume/<slug:slug>/share/', views_resume.share_resume, name='share_resume'),
    path('resume/<slug:slug>/analytics/', views_resume.resume_analytics, name='resume_analytics'),
    path('r/<str:share_token>/', views_resume.public_resume_view, name='public_resume'),
    
    # API endpoints
    path('api/resume/view/', views_resume.resume_view_api, name='resume_view_api'),
]
