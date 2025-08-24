// Resume Editor JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Constants and Variables
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    const resumeId = window.location.pathname.split('/').filter(Boolean).pop();
    let currentSectionId = null;
    
    // DOM Elements
    const sectionsListEl = document.getElementById('sections-list');
    const addSectionBtn = document.getElementById('add-section');
    const sectionEditor = document.getElementById('section-editor');
    const noSectionSelected = document.getElementById('no-section-selected');
    const sectionForm = document.getElementById('section-form');
    const sectionTitleDisplay = document.getElementById('section-title-display');
    const sectionEditForm = document.getElementById('section-edit-form');
    const sectionIdInput = document.getElementById('section-id');
    const sectionTitleInput = document.getElementById('section-title');
    const addItemBtn = document.getElementById('add-item');
    const itemsContainer = document.getElementById('items-container');
    const itemTemplate = document.getElementById('item-template');
    const saveResumeBtn = document.getElementById('save-resume');
    const saveSectionBtn = document.getElementById('save-section');
    const previewResumeBtn = document.getElementById('preview-resume');
    const exportPdfBtn = document.getElementById('export-pdf');
    
    // Event Listeners
    addSectionBtn.addEventListener('click', handleAddSection);
    addItemBtn.addEventListener('click', addNewItem);
    saveSectionBtn.addEventListener('click', saveCurrentSection);
    saveResumeBtn.addEventListener('click', saveEntireResume);
    previewResumeBtn.addEventListener('click', previewResume);
    exportPdfBtn.addEventListener('click', exportResumePdf);
    sectionsListEl.addEventListener('click', handleSectionClick);
    
    // Initialize section click handlers
    initializeSectionHandlers();
    
    // Functions
    function initializeSectionHandlers() {
        document.querySelectorAll('.section-item').forEach(el => {
            el.addEventListener('click', function(e) {
                if (!e.target.closest('.section-edit') && !e.target.closest('.section-delete')) {
                    const sectionId = el.dataset.sectionId;
                    loadSection(sectionId);
                }
            });
            
            const editBtn = el.querySelector('.section-edit');
            if (editBtn) {
                editBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const sectionId = el.dataset.sectionId;
                    loadSection(sectionId);
                });
            }
            
            const deleteBtn = el.querySelector('.section-delete');
            if (deleteBtn) {
                deleteBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const sectionId = el.dataset.sectionId;
                    deleteSection(sectionId);
                });
            }
        });
    }
    
    function loadSection(sectionId) {
        currentSectionId = sectionId;
        sectionIdInput.value = sectionId;
        
        // Show section form, hide placeholder
        noSectionSelected.classList.add('hidden');
        sectionForm.classList.remove('hidden');
        
        // Clear items container
        itemsContainer.innerHTML = '';
        
        // Fetch section data
        fetch(`/api/resume/section/${sectionId}/`)
            .then(response => response.json())
            .then(data => {
                sectionTitleInput.value = data.title;
                sectionTitleDisplay.textContent = data.title;
                
                // Add items
                if (data.items && data.items.length > 0) {
                    data.items.forEach(item => addItemToForm(item));
                }
            })
            .catch(error => {
                console.error('Error loading section:', error);
                alert('Failed to load section. Please try again.');
            });
    }
    
    function handleAddSection() {
        // Hide current section
        noSectionSelected.classList.add('hidden');
        sectionForm.classList.remove('hidden');
        
        // Clear form for new section
        currentSectionId = null;
        sectionIdInput.value = '';
        sectionTitleInput.value = 'New Section';
        sectionTitleDisplay.textContent = 'New Section';
        itemsContainer.innerHTML = '';
        
        // Add a blank item by default
        addNewItem();
    }
    
    function addNewItem() {
        const item = {
            id: '',
            title: '',
            subtitle: '',
            date_range: '',
            description: ''
        };
        addItemToForm(item);
    }
    
    function addItemToForm(item) {
        // Clone template
        const itemNode = document.importNode(itemTemplate.content, true).querySelector('.item-entry');
        
        // Set values
        const idInput = itemNode.querySelector('.item-id');
        const titleInput = itemNode.querySelector('.item-title');
        const subtitleInput = itemNode.querySelector('.item-subtitle');
        const dateRangeInput = itemNode.querySelector('.item-date-range');
        const descriptionInput = itemNode.querySelector('.item-description');
        
        idInput.value = item.id || '';
        titleInput.value = item.title || '';
        subtitleInput.value = item.subtitle || '';
        dateRangeInput.value = item.date_range || '';
        descriptionInput.value = item.description || '';
        
        // Add delete event listener
        const deleteBtn = itemNode.querySelector('.delete-item');
        deleteBtn.addEventListener('click', function() {
            itemNode.remove();
        });
        
        // Add to container
        itemsContainer.appendChild(itemNode);
    }
    
    function saveCurrentSection() {
        // Gather section data
        const sectionData = {
            section_id: sectionIdInput.value,
            section_data: {
                title: sectionTitleInput.value,
                items: []
            }
        };
        
        // Gather items data
        document.querySelectorAll('.item-entry').forEach((itemEl, index) => {
            sectionData.section_data.items.push({
                id: itemEl.querySelector('.item-id').value,
                title: itemEl.querySelector('.item-title').value,
                subtitle: itemEl.querySelector('.item-subtitle').value,
                date_range: itemEl.querySelector('.item-date-range').value,
                description: itemEl.querySelector('.item-description').value,
                order: index
            });
        });
        
        // Save via API
        fetch(`/api/resume/${resumeId}/section/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(sectionData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (!currentSectionId) {
                    // New section was created
                    currentSectionId = data.section_id;
                    sectionIdInput.value = data.section_id;
                    
                    // Add to sections list
                    const newSectionEl = document.createElement('div');
                    newSectionEl.className = 'section-item p-3 bg-gray-50 rounded cursor-pointer hover:bg-gray-100';
                    newSectionEl.dataset.sectionId = data.section_id;
                    newSectionEl.innerHTML = `
                        <div class="flex justify-between items-center">
                            <span class="font-medium">${sectionTitleInput.value}</span>
                            <div class="flex space-x-1">
                                <button class="text-gray-500 hover:text-gray-700 section-edit">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                                    </svg>
                                </button>
                                <button class="text-red-500 hover:text-red-700 section-delete">
                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                    </svg>
                                </button>
                            </div>
                        </div>
                    `;
                    sectionsListEl.appendChild(newSectionEl);
                    initializeSectionHandlers();
                } else {
                    // Update section title in the list
                    const sectionEl = document.querySelector(`.section-item[data-section-id="${currentSectionId}"]`);
                    if (sectionEl) {
                        sectionEl.querySelector('span').textContent = sectionTitleInput.value;
                    }
                }
                
                // Update section title display
                sectionTitleDisplay.textContent = sectionTitleInput.value;
                
                // Show success message
                showNotification('Section saved successfully', 'success');
            } else {
                showNotification('Failed to save section', 'error');
            }
        })
        .catch(error => {
            console.error('Error saving section:', error);
            showNotification('Error saving section', 'error');
        });
    }
    
    function deleteSection(sectionId) {
        if (!confirm('Are you sure you want to delete this section? This action cannot be undone.')) {
            return;
        }
        
        fetch(`/api/resume/section/${sectionId}/delete/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Remove from DOM
                const sectionEl = document.querySelector(`.section-item[data-section-id="${sectionId}"]`);
                if (sectionEl) {
                    sectionEl.remove();
                }
                
                // If this was the current section, reset view
                if (currentSectionId === sectionId) {
                    currentSectionId = null;
                    sectionForm.classList.add('hidden');
                    noSectionSelected.classList.remove('hidden');
                }
                
                showNotification('Section deleted successfully', 'success');
            } else {
                showNotification('Failed to delete section', 'error');
            }
        })
        .catch(error => {
            console.error('Error deleting section:', error);
            showNotification('Error deleting section', 'error');
        });
    }
    
    function saveEntireResume() {
        // Get contact info
        const contactData = {
            full_name: document.getElementById('full_name').value,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            location: document.getElementById('location').value
        };
        
        // Save via API
        fetch(`/api/resume/${resumeId}/save/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                contact: contactData
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Resume saved successfully', 'success');
            } else {
                showNotification('Failed to save resume', 'error');
            }
        })
        .catch(error => {
            console.error('Error saving resume:', error);
            showNotification('Error saving resume', 'error');
        });
    }
    
    function previewResume() {
        window.open(`/resume/${resumeId}/preview/`, '_blank');
    }
    
    function exportResumePdf() {
        window.location.href = `/resume/${resumeId}/export-pdf/`;
    }
    
    function handleSectionClick(e) {
        const sectionItem = e.target.closest('.section-item');
        if (!sectionItem) return;
        
        // Don't process if click was on a button
        if (e.target.closest('button')) return;
        
        const sectionId = sectionItem.dataset.sectionId;
        loadSection(sectionId);
    }
    
    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 px-6 py-3 rounded-md shadow-md ${
            type === 'success' ? 'bg-green-500' : 
            type === 'error' ? 'bg-red-500' : 
            'bg-blue-500'
        } text-white z-50`;
        notification.textContent = message;
        
        // Add to DOM
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.add('opacity-0', 'transition-opacity');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
});
