// Modal functionality for vacancies_description.html
document.addEventListener('DOMContentLoaded', function() {
    const applyBtn = document.getElementById('applyBtn');
    const modal = document.getElementById('applicationModal');
    const closeModal = document.getElementById('closeModal');

    if (applyBtn && modal) {
        applyBtn.addEventListener('click', function() {
            modal.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }

    if (closeModal && modal) {
        closeModal.addEventListener('click', function() {
            modal.classList.remove('active');
            document.body.style.overflow = 'auto';
        });
    }

    // Close modal when clicking outside
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('active');
                document.body.style.overflow = 'auto';
            }
        });
    }

    // File upload display
    const cvInput = document.getElementById('cv');
    if (cvInput) {
        cvInput.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            const placeholder = document.querySelector('.file-placeholder');
            if (fileName && placeholder) {
                placeholder.textContent = fileName;
                placeholder.style.color = '#374151';
            }
        });
    }
});