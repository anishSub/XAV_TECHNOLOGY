// Scroll to Top Button
const scrollTopBtn = document.getElementById('scrollTopBtn');

if (scrollTopBtn) {
    // Show/hide scroll button
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollTopBtn.style.display = 'flex';
        } else {
            scrollTopBtn.style.display = 'none';
        }
    });

    // Scroll to top on click
    scrollTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Profile Dropdown Toggle
const profileButton = document.getElementById('profileButton');
const profileDropdown = document.getElementById('profileDropdown');

if (profileButton && profileDropdown) {
    profileButton.addEventListener('click', function(e) {
        e.stopPropagation();
        profileDropdown.classList.toggle('active');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!profileDropdown.contains(e.target)) {
            profileDropdown.classList.remove('active');
        }
    });

    // Close dropdown when pressing Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            profileDropdown.classList.remove('active');
        }
    });
}

// Auto-hide messages after 5 seconds
const messagesContainer = document.querySelector('.messages-container');
if (messagesContainer) {
    setTimeout(function() {
        const alerts = messagesContainer.querySelectorAll('.alert');
        alerts.forEach(alert => {
            alert.style.animation = 'slideOut 0.3s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(400px)';
            setTimeout(() => alert.remove(), 300);
        });
        setTimeout(() => messagesContainer.remove(), 400);
    }, 5000);
}

// Search functionality (optional - you can enhance this later)
const searchInput = document.querySelector('.search-input');
const searchBtn = document.querySelector('.search-btn');

if (searchInput && searchBtn) {
    searchBtn.addEventListener('click', function() {
        const searchQuery = searchInput.value.trim();
        if (searchQuery) {
            // You can add search functionality here
            console.log('Searching for:', searchQuery);
            // Example: window.location.href = `/search/?q=${encodeURIComponent(searchQuery)}`;
        }
    });

    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchBtn.click();
        }
    });
}