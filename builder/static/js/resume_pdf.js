/**
 * PDF generation and export handling with fallback for WeasyPrint errors
 */

// Function to generate a PDF and handle errors gracefully
function generateResumePdf(resumeSlug, options = {}) {
    // Default options
    const defaultOptions = {
        font: 'helvetica',
        color: 'blue',
        onSuccess: function(pdfUrl) {
            window.open(pdfUrl, '_blank');
        },
        onError: function(error) {
            alert('Error generating PDF: ' + error);
        }
    };
    
    // Merge options
    const settings = {...defaultOptions, ...options};
    
    // Show loading state
    document.getElementById('pdfSpinner').classList.remove('hidden');
    document.getElementById('exportPdfButton').disabled = true;
    
    // Build URL with parameters
    let url = `/resume/${resumeSlug}/generate-pdf/?font=${settings.font}&color=${settings.color}`;
    if (settings.templateId) {
        url += `&template_id=${settings.templateId}`;
    }
    
    // Make AJAX request
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Hide loading state
            document.getElementById('pdfSpinner').classList.add('hidden');
            document.getElementById('exportPdfButton').disabled = false;
            
            if (data.success) {
                // Success - open PDF
                settings.onSuccess(data.pdf_url);
            } else {
                // Error with fallback
                if (data.html_fallback && data.fallback_url) {
                    // If there's a fallback URL, open it in a new tab
                    window.open(data.fallback_url, '_blank');
                } else {
                    // Otherwise show the error
                    settings.onError(data.error);
                }
            }
        })
        .catch(error => {
            // Hide loading state
            document.getElementById('pdfSpinner').classList.add('hidden');
            document.getElementById('exportPdfButton').disabled = false;
            
            // Show error
            settings.onError('Network error, please try again later.');
            console.error('PDF generation error:', error);
        });
}
