document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM ready, initializing...');
    
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
    console.log('Initializing FAQ...');
    
    const faqItems = document.querySelectorAll('.faq-item');
    console.log('FAQ items found:', faqItems.length);
    
    if (faqItems.length === 0) {
        console.error('No FAQ items found!');
        return;
    }
    
    faqItems.forEach((item, index) => {
        const question = item.querySelector('.faq-question');
        
        if (question) {
            console.log(`Adding listener to FAQ ${index}`);
            
            question.addEventListener('click', (e) => {
                e.preventDefault(); // Prevent button default behavior
                console.log(`FAQ ${index} clicked`);
                
                const isActive = item.classList.contains('active');
                
                // Close all items
                faqItems.forEach(otherItem => {
                    otherItem.classList.remove('active');
                    const otherIcon = otherItem.querySelector('.faq-icon');
                    if (otherIcon) otherIcon.textContent = '+';
                });
                
                // Open clicked item if it wasn't active
                if (!isActive) {
                    item.classList.add('active');
                    const icon = item.querySelector('.faq-icon');
                    if (icon) icon.textContent = '−';
                }
            });
        }
    });
    
    console.log('FAQ initialization complete!');
});