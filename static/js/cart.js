/**
 * CS50 Shop - Cart Functionality
 */

// Add to cart function
function addToCart(productId, quantity = 1, callback = null) {
    // Make an AJAX request to add the item to the cart
    fetch('/api/cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: parseInt(quantity)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart count in the navigation bar
            updateCartCount();
            
            // Show success message
            showAlert('Success', 'Product added to cart', 'success');
            
            // Execute callback if provided
            if (callback && typeof callback === 'function') {
                callback();
            }
        } else {
            // Show error message
            showAlert('Error', data.message || 'Failed to add product to cart', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error', 'Failed to add product to cart', 'danger');
    });
}

// Update cart count in the navigation
function updateCartCount() {
    // Fetch the current cart count
    fetch('/api/cart')
    .then(response => response.json())
    .then(data => {
        const cartCountElement = document.querySelector('.cart-count');
        if (cartCountElement) {
            cartCountElement.textContent = data.count;
            
            // Animate the count change
            cartCountElement.classList.add('animate__animated', 'animate__bounceIn');
            setTimeout(() => {
                cartCountElement.classList.remove('animate__animated', 'animate__bounceIn');
            }, 1000);
        }
    })
    .catch(error => {
        console.error('Error updating cart count:', error);
    });
}

// Remove item from cart
function removeFromCart(productId, callback = null) {
    fetch('/api/cart', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            product_id: productId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update cart count
            updateCartCount();
            
            // Show success message
            showAlert('Success', 'Product removed from cart', 'success');
            
            // Execute callback if provided
            if (callback && typeof callback === 'function') {
                callback();
            }
        } else {
            showAlert('Error', data.message || 'Failed to remove product from cart', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error', 'Failed to remove product from cart', 'danger');
    });
}

// Update cart item quantity
function updateCartItemQuantity(productId, quantity, callback = null) {
    if (quantity <= 0) {
        removeFromCart(productId, callback);
        return;
    }
    
    fetch('/update_cart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'product_id': productId,
            'quantity': quantity
        })
    })
    .then(response => {
        if (response.ok) {
            // Show success message
            showAlert('Success', 'Cart updated', 'success');
            
            // Execute callback if provided
            if (callback && typeof callback === 'function') {
                callback();
            }
        } else {
            showAlert('Error', 'Failed to update cart', 'danger');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error', 'Failed to update cart', 'danger');
    });
}

// Show alert message
function showAlert(title, message, type = 'info') {
    // Create alert container if it doesn't exist
    let alertContainer = document.querySelector('.alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.className = 'alert-container position-fixed top-0 end-0 p-3';
        alertContainer.style.zIndex = '1050';
        document.body.appendChild(alertContainer);
    }
    
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.role = 'alert';
    
    // Add alert content
    alert.innerHTML = `
        <strong>${title}</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Add alert to container
    alertContainer.appendChild(alert);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            alert.remove();
        }, 150);
    }, 3000);
}

// Initialize cart functionality when the DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to "Add to Cart" buttons
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.dataset.productId;
            addToCart(productId);
        });
    });
    
    // Update cart count on page load
    updateCartCount();
});