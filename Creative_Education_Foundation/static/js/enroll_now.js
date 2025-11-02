// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Variable to store selected wallet
    let selectedWallet = null;

    // Get all wallet cards
    const walletCards = document.querySelectorAll('.wallet-card');
    const proceedBtn = document.getElementById('proceed-btn');

    // Add click event listener to each wallet card
    walletCards.forEach(card => {
        card.addEventListener('click', function() {
            // Remove selected class from all cards
            walletCards.forEach(c => c.classList.remove('selected'));
            
            // Add selected class to clicked card
            this.classList.add('selected');
            
            // Store selected wallet
            selectedWallet = this.getAttribute('data-wallet');
            
            // Enable proceed button
            proceedBtn.disabled = false;
            
            console.log('Selected wallet:', selectedWallet);
        });
    });

    // Add click event listener to proceed button
    proceedBtn.addEventListener('click', function() {
        if (selectedWallet) {
            // Get order details
            const className = document.getElementById('class-name').textContent;
            const productId = document.getElementById('product-id').textContent;
            const price = document.getElementById('price').textContent;
            const discount = document.getElementById('discount').textContent;
            const total = document.getElementById('total').textContent;

            // Log payment initiation
            console.log('Payment initiated with:', {
                wallet: selectedWallet,
                className: className,
                productId: productId,
                price: price,
                discount: discount,
                total: total
            });

            // Show confirmation message
            const walletName = selectedWallet.toUpperCase();
            alert(`Proceeding with ${walletName} payment for Rs. ${total}...`);

            // TODO: Replace with actual payment gateway integration
            // Example redirects:
            if (selectedWallet === 'esewa') {
                // window.location.href = '/payment/esewa/';
                console.log('Redirecting to eSewa payment gateway...');
            } else if (selectedWallet === 'khalti') {
                // window.location.href = '/payment/khalti/';
                console.log('Redirecting to Khalti payment gateway...');
            }
        }
    });

    // Optional: Get URL parameters to pre-fill class information
    function getUrlParameter(name) {
        name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
        const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
        const results = regex.exec(location.search);
        return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
    }

    // Pre-fill class information if passed via URL
    const classNameParam = getUrlParameter('class');
    const productIdParam = getUrlParameter('id');
    const priceParam = getUrlParameter('price');

    if (classNameParam) {
        document.getElementById('class-name').textContent = classNameParam;
    }
    if (productIdParam) {
        document.getElementById('product-id').textContent = productIdParam;
    }
    if (priceParam) {
        document.getElementById('price').textContent = priceParam;
        document.getElementById('total').textContent = priceParam; // Assuming no discount
    }

    // Add keyboard navigation for accessibility
    walletCards.forEach(card => {
        card.setAttribute('tabindex', '0');
        
        card.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.click();
            }
        });
    });

    // Add enter key functionality to proceed button
    proceedBtn.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            this.click();
        }
    });
});