// Enhanced Resume Editor JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Modal Functionality
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        // Reset form if adding new item
        const form = modal.querySelector('form');
        if (form && form.querySelector('input[name="action"]').value === 'add') {
            form.reset();
            
            // Reset any hidden ID fields
            const idField = form.querySelector('input[type="hidden"][name="id"]');
            if (idField) idField.value = '';
            
            // Reset submit button text
            const submitText = modal.querySelector('.btn-text');
            if (submitText) {
                submitText.textContent = submitText.textContent.replace('Save Changes', 'Add');
            }
        }
        
        modal.style.display = 'block';
        document.body.classList.add('modal-open');
    };
    
    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;
        
        modal.style.display = 'none';
        document.body.classList.remove('modal-open');
    };
    
    // Close modal when clicking outside
    window.onclick = function(event) {
        const modals = document.getElementsByClassName('modal');
        for (let i = 0; i < modals.length; i++) {
            if (event.target === modals[i]) {
                closeModal(modals[i].id);
            }
        }
    };
    
    // Handle current job checkbox
    const currentCheckbox = document.getElementById('current');
    const endDateInput = document.getElementById('exp_end_date');
    
    if (currentCheckbox && endDateInput) {
        currentCheckbox.addEventListener('change', function() {
            endDateInput.disabled = this.checked;
            if (this.checked) {
                endDateInput.value = '';
            }
        });
    }
    
    // Edit functions
    window.editEducation = function(id) {
        // Set the form action to edit
        const form = document.getElementById('educationForm');
        form.querySelector('input[name="action"]').value = 'edit';
        form.querySelector('#education_id').value = id;
        
        // Change the button text
        document.getElementById('educationSubmitText').textContent = 'Save Changes';
        
        // Get the education data and populate the form
        fetch(`/api/resume/education/${id}/`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('institution').value = data.institution || '';
                document.getElementById('degree').value = data.degree || '';
                document.getElementById('field_of_study').value = data.field_of_study || '';
                document.getElementById('start_date').value = data.start_date || '';
                document.getElementById('end_date').value = data.end_date || '';
                document.getElementById('description').value = data.description || '';
                
                // Open the modal
                openModal('educationModal');
            })
            .catch(error => {
                console.error('Error fetching education data:', error);
                showNotification('Error loading education data', 'error');
            });
    };
    
    window.editExperience = function(id) {
        // Set the form action to edit
        const form = document.getElementById('experienceForm');
        form.querySelector('input[name="action"]').value = 'edit';
        form.querySelector('#experience_id').value = id;
        
        // Change the button text
        document.getElementById('experienceSubmitText').textContent = 'Save Changes';
        
        // Get the experience data and populate the form
        fetch(`/api/resume/experience/${id}/`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('company').value = data.company || '';
                document.getElementById('position').value = data.position || '';
                document.getElementById('location').value = data.location || '';
                document.getElementById('exp_start_date').value = data.start_date || '';
                document.getElementById('exp_end_date').value = data.end_date || '';
                document.getElementById('current').checked = data.current || false;
                document.getElementById('exp_description').value = data.description || '';
                
                // Handle current checkbox
                if (data.current) {
                    document.getElementById('exp_end_date').disabled = true;
                } else {
                    document.getElementById('exp_end_date').disabled = false;
                }
                
                // Open the modal
                openModal('experienceModal');
            })
            .catch(error => {
                console.error('Error fetching experience data:', error);
                showNotification('Error loading experience data', 'error');
            });
    };
    
    window.editProject = function(id) {
        // Set the form action to edit
        const form = document.getElementById('projectForm');
        form.querySelector('input[name="action"]').value = 'edit';
        form.querySelector('#project_id').value = id;
        
        // Change the button text
        document.getElementById('projectSubmitText').textContent = 'Save Changes';
        
        // Get the project data and populate the form
        fetch(`/api/resume/project/${id}/`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('project_title').value = data.title || '';
                document.getElementById('project_description').value = data.description || '';
                document.getElementById('technologies').value = data.technologies || '';
                document.getElementById('url').value = data.url || '';
                document.getElementById('project_start_date').value = data.start_date || '';
                document.getElementById('project_end_date').value = data.end_date || '';
                
                // Open the modal
                openModal('projectModal');
            })
            .catch(error => {
                console.error('Error fetching project data:', error);
                showNotification('Error loading project data', 'error');
            });
    };
    
    window.editCertification = function(id) {
        // Set the form action to edit
        const form = document.getElementById('certificationForm');
        form.querySelector('input[name="action"]').value = 'edit';
        form.querySelector('#certification_id').value = id;
        
        // Change the button text
        document.getElementById('certificationSubmitText').textContent = 'Save Changes';
        
        // Get the certification data and populate the form
        fetch(`/api/resume/certification/${id}/`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('cert_name').value = data.name || '';
                document.getElementById('issuer').value = data.issuer || '';
                document.getElementById('date_issued').value = data.date_issued || '';
                document.getElementById('expiration_date').value = data.expiration_date || '';
                document.getElementById('credential_id').value = data.credential_id || '';
                document.getElementById('credential_url').value = data.credential_url || '';
                
                // Open the modal
                openModal('certificationModal');
            })
            .catch(error => {
                console.error('Error fetching certification data:', error);
                showNotification('Error loading certification data', 'error');
            });
    };
    
    // PDF Generation
    window.generateResumePdf = function(resumeSlug) {
        const button = document.getElementById('exportPdfButton');
        const spinner = document.getElementById('pdfSpinner');
        const buttonText = button.querySelector('.btn-text');
        
        // Show loading state
        spinner.classList.remove('hidden');
        buttonText.textContent = 'Generating PDF...';
        button.disabled = true;
        
        // Generate PDF
        fetch(`/resume/${resumeSlug}/export-pdf/`, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('PDF generation failed');
            }
            return response.blob();
        })
        .then(blob => {
            // Create download link
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `resume_${resumeSlug}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            
            // Reset button
            spinner.classList.add('hidden');
            buttonText.textContent = 'Export as PDF';
            button.disabled = false;
            
            showNotification('PDF generated successfully!', 'success');
        })
        .catch(error => {
            console.error('Error generating PDF:', error);
            
            // Reset button
            spinner.classList.add('hidden');
            buttonText.textContent = 'Export as PDF';
            button.disabled = false;
            
            showNotification('Failed to generate PDF. Please try again.', 'error');
        });
    };
    
    // Notification system
    window.showNotification = function(message, type = 'info') {
        // Create notification container if it doesn't exist
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.style.position = 'fixed';
            container.style.top = '1rem';
            container.style.right = '1rem';
            container.style.zIndex = '1000';
            container.style.display = 'flex';
            container.style.flexDirection = 'column';
            container.style.gap = '0.5rem';
            document.body.appendChild(container);
        }
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.style.padding = '0.75rem 1.25rem';
        notification.style.borderRadius = '0.375rem';
        notification.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
        notification.style.display = 'flex';
        notification.style.alignItems = 'center';
        notification.style.animation = 'slideIn 0.3s ease';
        
        // Set color based on type
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#10b981';
                notification.style.color = 'white';
                break;
            case 'error':
                notification.style.backgroundColor = '#ef4444';
                notification.style.color = 'white';
                break;
            case 'warning':
                notification.style.backgroundColor = '#f59e0b';
                notification.style.color = 'white';
                break;
            default:
                notification.style.backgroundColor = '#3b82f6';
                notification.style.color = 'white';
        }
        
        notification.textContent = message;
        
        // Add to container
        container.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.3s ease';
            
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    };
    
    // Form validation enhancement
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            // Add visual feedback
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.classList.add('border-red-500');
                    
                    // Add error message if it doesn't exist
                    const errorMsg = field.parentNode.querySelector('.error-message');
                    if (!errorMsg) {
                        const msg = document.createElement('p');
                        msg.className = 'error-message text-xs text-red-500 mt-1';
                        msg.textContent = 'This field is required';
                        field.parentNode.appendChild(msg);
                    }
                } else {
                    field.classList.remove('border-red-500');
                    const errorMsg = field.parentNode.querySelector('.error-message');
                    if (errorMsg) errorMsg.remove();
                }
            });
            
            if (!valid) {
                event.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });
    });
    
    // Add input event listeners to clear errors on typing
    document.querySelectorAll('input, textarea, select').forEach(field => {
        field.addEventListener('input', function() {
            field.classList.remove('border-red-500');
            const errorMsg = field.parentNode.querySelector('.error-message');
            if (errorMsg) errorMsg.remove();
        });
    });
    
    // Add smooth scroll effect for better UX
    document.querySelectorAll('.editor-section').forEach(section => {
        const sectionHeader = section.querySelector('.section-header');
        if (sectionHeader) {
            sectionHeader.addEventListener('click', function() {
                section.scrollIntoView({ behavior: 'smooth', block: 'start' });
            });
        }
    });
    
    // Handle date input formatting
    document.querySelectorAll('input[type="date"]').forEach(dateInput => {
        dateInput.addEventListener('blur', function() {
            if (!this.value) return;
            
            try {
                const date = new Date(this.value);
                if (!isNaN(date.getTime())) {
                    // Valid date, format it nicely if needed
                    // this.value = date.toISOString().split('T')[0];
                }
            } catch (e) {
                console.error('Date parsing error:', e);
            }
        });
    });
});

// Function to handle PDF generation
function generateResumePdf(resumeSlug) {
    const button = document.getElementById('exportPdfButton');
    const spinner = document.getElementById('pdfSpinner');
    const buttonText = button.querySelector('.btn-text');
    
    // Show loading state
    spinner.classList.remove('hidden');
    buttonText.textContent = 'Generating PDF...';
    button.disabled = true;
    
    // Generate PDF
    fetch(`/resume/${resumeSlug}/export-pdf/`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('PDF generation failed');
        }
        return response.blob();
    })
    .then(blob => {
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        a.download = `resume_${resumeSlug}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        
        // Reset button
        spinner.classList.add('hidden');
        buttonText.textContent = 'Export as PDF';
        button.disabled = false;
        
        showNotification('PDF generated successfully!', 'success');
    })
    .catch(error => {
        console.error('Error generating PDF:', error);
        
        // Reset button
        spinner.classList.add('hidden');
        buttonText.textContent = 'Export as PDF';
        button.disabled = false;
        
        showNotification('Failed to generate PDF. Please try again.', 'error');
    });
}
