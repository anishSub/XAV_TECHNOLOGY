// Scroll to top functionality
const scrollTopBtn = document.getElementById('scrollTopBtn');

if (scrollTopBtn) {
    scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// FAQ Accordion Functionality
document.addEventListener('DOMContentLoaded', function() {
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        
        question.addEventListener('click', () => {
            // Close other items
            faqItems.forEach(otherItem => {
                if (otherItem !== item && otherItem.classList.contains('active')) {
                    otherItem.classList.remove('active');
                    const otherIcon = otherItem.querySelector('.faq-icon');
                    otherIcon.textContent = '+';
                }
            });
            
            // Toggle current item
            item.classList.toggle('active');
            const icon = item.querySelector('.faq-icon');
            
            if (item.classList.contains('active')) {
                icon.textContent = '−';
            } else {
                icon.textContent = '+';
            }
        });
    });
});