// RO2 Table Converter - Internal Tool JavaScript

// Disable Dropzone auto-discovery
Dropzone.autoDiscover = false;

// Initialize Dropzone
const dropzone = new Dropzone("#file-dropzone", {
    url: "/upload",
    paramName: "files",
    maxFilesize: 100,
    acceptedFiles: ".ct,.xlsx",
    addRemoveLinks: false,
    dictDefaultMessage: '',
    autoProcessQueue: true,
    uploadMultiple: true,
    parallelUploads: 10,
    maxFiles: 50,
    
    init: function() {
        this.on("sending", function(file, xhr, formData) {
            showLoading();
            showProgress();
        });
        
        this.on("success", function(files, response) {
            hideLoading();
            hideProgress();
            handleUploadResponse(response);
            this.removeAllFiles();
        });
        
        this.on("error", function(file, errorMessage) {
            hideLoading();
            hideProgress();
            showError("Upload failed: " + errorMessage);
            this.removeAllFiles();
        });
    }
});

/**
 * Show loading modal
 */
function showLoading() {
    const modal = document.getElementById('loading-modal');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
}

/**
 * Hide loading modal
 */
function hideLoading() {
    const modal = document.getElementById('loading-modal');
    modal.classList.add('hidden');
    modal.classList.remove('flex');
}

/**
 * Show progress bar
 */
function showProgress() {
    const container = document.getElementById('progress-container');
    container.classList.remove('hidden');
    
    // Reset progress
    const progressBar = document.getElementById('conversion-progress');
    const progressText = document.getElementById('progress-text');
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
}

/**
 * Hide progress bar
 */
function hideProgress() {
    const container = document.getElementById('progress-container');
    container.classList.add('hidden');
}

/**
 * Update progress bar
 */
function updateProgress(percent) {
    const progressBar = document.getElementById('conversion-progress');
    const progressText = document.getElementById('progress-text');
    progressBar.style.width = percent + '%';
    progressText.textContent = percent + '%';
}

/**
 * Show error notification
 */
function showError(message) {
    showToast(message, 'error');
}

/**
 * Show success notification
 */
function showSuccess(message) {
    showToast(message, 'success');
}

/**
 * Show toast notification
 */
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    const bgColor = type === 'error' ? 'bg-red-600' : 'bg-green-600';
    const icon = type === 'error' ? 'fa-exclamation-circle' : 'fa-check-circle';
    
    toast.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-4 rounded-lg shadow-lg z-50 transform transition-transform duration-300`;
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${icon} mr-2"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Auto-remove after 5 seconds for errors, 3 for success
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.add('translate-x-full');
            setTimeout(() => toast.remove(), 300);
        }
    }, type === 'error' ? 5000 : 3000);
}

/**
 * Handle upload response
 */
function handleUploadResponse(response) {
    console.log('Upload response:', response);
    
    if (response.success) {
        showResults(response.results);
        showSuccess(`Successfully converted ${response.results.length} file(s)`);
    } else {
        showError(response.error || 'Unknown error occurred');
    }
}

/**
 * Show conversion results
 */
function showResults(results) {
    const container = document.getElementById('results-container');
    const resultsList = document.getElementById('results-list');
    
    // Clear previous results
    resultsList.innerHTML = '';
    
    // Create results
    results.forEach(result => {
        const resultElement = document.createElement('div');
        resultElement.className = 'bg-gray-700 rounded-lg p-4 border border-gray-600';
        
        const statusIcon = result.success ? 
            '<i class="fas fa-check-circle text-green-500"></i>' : 
            '<i class="fas fa-exclamation-triangle text-red-500"></i>';
            
        const downloadButton = result.success ? 
            `<a href="/download/${encodeURIComponent(result.output_file)}" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm transition-colors inline-flex items-center">
                <i class="fas fa-download mr-1"></i>Download
            </a>` : '';
        
        const statusBadge = result.success ? 
            `<span class="bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs">${result.output_file}</span>` : 
            `<span class="bg-red-500/20 text-red-400 px-2 py-1 rounded text-xs">Failed</span>`;
        
        resultElement.innerHTML = `
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                    ${statusIcon}
                    <span class="text-white font-medium">${result.input_file}</span>
                </div>
                <div class="flex items-center space-x-2">
                    ${statusBadge}
                    ${downloadButton}
                </div>
            </div>
            ${result.error ? `<p class="text-red-400 text-sm mt-2">${result.error}</p>` : ''}
        `;
        
        resultsList.appendChild(resultElement);
    });
    
    // Show results container
    container.classList.remove('hidden');
}

/**
 * Clear results
 */
function clearResults() {
    const container = document.getElementById('results-container');
    const resultsList = document.getElementById('results-list');
    
    resultsList.innerHTML = '';
    container.classList.add('hidden');
}

/**
 * Download file with debug logging
 */
function downloadFile(filename) {
    console.log('Downloading file:', filename);
    const url = `/download/${encodeURIComponent(filename)}`;
    console.log('Download URL:', url);
    
    // Create temporary link and click it
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Progress simulation for better UX
function simulateProgress() {
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress >= 95) {
            clearInterval(interval);
            progress = 95;
        }
        updateProgress(Math.round(progress));
    }, 200);
    
    return interval;
}

// Close modal when clicking background
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('loading-modal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                hideLoading();
            }
        });
    }
});

console.log('🚀 RO2 Table Converter - Internal Tool JavaScript loaded');
console.log('🎨 Framework: Tailwind CSS with Dark Mode');
console.log('📁 Dropzone initialized for file uploads');
