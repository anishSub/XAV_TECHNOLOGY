// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Get all day items
    const dayItems = document.querySelectorAll('.day-item');
    
    // Add click event to each day item
    dayItems.forEach(item => {
        const header = item.querySelector('.day-header-simple');
        
        if (header) {
            header.addEventListener('click', function(e) {
                e.stopPropagation();
                
                // Toggle active class
                const isActive = item.classList.contains('active');
                
                // Remove active class from all items
                dayItems.forEach(i => i.classList.remove('active'));
                
                // Add active class to clicked item if it wasn't active
                if (!isActive) {
                    item.classList.add('active');
                }
            });
        }
    });
});