// ==========================================================================
// Main JavaScript - Smart Contact Book Application
// Premium SaaS UI Functions
// ==========================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initDarkMode();
    initSidebar();
    setupFavoriteToggles();
    setupToastNotifications();
    setupSearchDebounce();
    setupFormValidation();
});

// ==========================================================================
// Dark Mode Management
// ==========================================================================

function initDarkMode() {
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;
    const icon = themeToggle?.querySelector('.fa-moon, .fa-sun');
    
    // Check for saved theme preference or default to light mode
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    if (currentTheme === 'dark') {
        body.classList.add('dark');
        if (icon) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        }
    }
    
    // Toggle theme on button click
    themeToggle?.addEventListener('click', function() {
        body.classList.toggle('dark');
        
        const isDark = body.classList.contains('dark');
        const newTheme = isDark ? 'dark' : 'light';
        
        // Update icon
        if (icon) {
            if (isDark) {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
        }
        
        // Save theme preference
        localStorage.setItem('theme', newTheme);
        
        // Dispatch event for other components to react
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { isDark } }));
    });
}

// ==========================================================================
// Sidebar Management
// ==========================================================================

function initSidebar() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const closeSidebar = document.getElementById('closeSidebar');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    // Toggle sidebar
    sidebarToggle?.addEventListener('click', function() {
        sidebar?.classList.toggle('-translate-x-full');
        overlay?.classList.toggle('hidden');
    });
    
    // Close sidebar when clicking overlay
    overlay?.addEventListener('click', function() {
        sidebar?.classList.add('-translate-x-full');
        this.classList.add('hidden');
    });

    closeSidebar?.addEventListener('click', function() {
        sidebar?.classList.add('-translate-x-full');
        overlay?.classList.add('hidden');
    });
    
    // Handle responsive sidebar
    handleResponsiveSidebar();
    window.addEventListener('resize', handleResponsiveSidebar);
}

function handleResponsiveSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    if (window.innerWidth >= 1024) {
        // Desktop - show sidebar
        sidebar?.classList.remove('-translate-x-full');
        overlay?.classList.add('hidden');
    } else {
        // Mobile - hide sidebar by default
        sidebar?.classList.add('-translate-x-full');
        overlay?.classList.add('hidden');
    }
}

// ==========================================================================
// Favorite Toggle (AJAX)
// ==========================================================================

function setupFavoriteToggles() {
    const favoriteButtons = document.querySelectorAll('.toggle-favorite');
    
    favoriteButtons.forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            
            const contactId = this.dataset.contactId;
            const isFavorite = this.dataset.isFavorite === 'true';
            const url = `/contacts/${contactId}/favorite/`;
            
            try {
                const formData = new FormData();
                formData.append('csrfmiddlewaretoken', getCSRFToken());
                
                const response = await fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Update button appearance
                    updateFavoriteButton(this, data.is_favorite);
                    
                    // Show success notification
                    showToast(
                        data.is_favorite ? 'Added to favorites! ⭐' : 'Removed from favorites!',
                        'success'
                    );
                }
            } catch (error) {
                console.error('Error toggling favorite:', error);
                showToast('An error occurred. Please try again.', 'error');
            }
        });
    });
}

function updateFavoriteButton(button, isFavorite) {
    const icon = button.querySelector('i');
    
    if (isFavorite) {
        button.classList.remove('text-gray-400', 'hover:text-yellow-500');
        button.classList.add('text-yellow-500');
        icon.classList.remove('fa-regular');
        icon.classList.add('fa-solid');
    } else {
        button.classList.remove('text-yellow-500');
        button.classList.add('text-gray-400', 'hover:text-yellow-500');
        icon.classList.remove('fa-solid');
        icon.classList.add('fa-regular');
    }
    
    button.dataset.isFavorite = isFavorite;
}

// ==========================================================================
// Toast Notifications
// ==========================================================================

function setupToastNotifications() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast-notification ${getToastClass(type)}`;
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="fas ${getToastIcon(type)} me-2"></i>
            <span>${message}</span>
        </div>
        <button onclick="this.parentElement.remove()" class="ms-2 text-gray-400 hover:text-gray-600">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'fixed top-4 right-4 z-50 space-y-2';
    document.body.appendChild(container);
    return container;
}

function getToastClass(type) {
    const classes = {
        success: 'bg-green-500 text-white shadow-lg shadow-green-500/30',
        error: 'bg-red-500 text-white shadow-lg shadow-red-500/30',
        warning: 'bg-yellow-500 text-white shadow-lg shadow-yellow-500/30',
        info: 'bg-blue-500 text-white shadow-lg shadow-blue-500/30'
    };
    return classes[type] || classes.info;
}

function getToastIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-exclamation-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}

// ==========================================================================
// Search Debounce
// ==========================================================================

function setupSearchDebounce() {
    const searchInput = document.querySelector('#searchInput');
    
    if (searchInput) {
        let debounceTimer;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                // Could trigger AJAX search here
                console.log('Searching for:', this.value);
            }, 300);
        });
    }
}

// ==========================================================================
// Form Validation
// ==========================================================================

function setupFormValidation() {
    const forms = document.querySelectorAll('form[data-validate]');
    
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
        
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                if (this.classList.contains('error')) {
                    validateField(this);
                }
            });
        });
        
        form.addEventListener('submit', function(e) {
            let isValid = true;
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showToast('Please fix the errors in the form.', 'error');
            }
        });
    });
}

function validateField(field) {
    const value = field.value.trim();
    const isValid = value.length > 0;
    
    if (!isValid) {
        field.classList.add('error');
        field.classList.add('border-red-500');
        field.classList.remove('border-gray-300');
    } else {
        field.classList.remove('error');
        field.classList.remove('border-red-500');
        field.classList.add('border-gray-300');
    }
    
    return isValid;
}

// ==========================================================================
// Utility Functions
// ==========================================================================

function getCSRFToken() {
    return document.cookie.split('; ').reduce((r, v) => {
        const parts = v.split('=');
        return parts[0] === 'csrftoken' ? decodeURIComponent(parts[1]) : r;
    }, '');
}

function confirmAction(message = 'Are you sure?') {
    return window.confirm(message);
}

// Smooth scroll to element
function scrollToElement(element, offset = 0) {
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - offset;
    
    window.scrollTo({
        top: offsetPosition,
        behavior: 'smooth'
    });
}
