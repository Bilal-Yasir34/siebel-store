// ===== Document Ready =====
document.addEventListener('DOMContentLoaded', () => {
  setupArrivalArrows();
  setInterval(moveGallery, 5000);
  setInterval(shakeButton, 5000);
  updateCartBadgeCount(); // Live cart badge sync on page load

  // FAQ Accordion Clicks
  document.querySelectorAll('.faq-question').forEach(button => {
    button.addEventListener('click', () => {
      const item = button.parentElement;
      item.classList.toggle('active');
    });
  });
});

// ====== New Arrivals Carousel Arrows ======
function setupArrivalArrows() {
  const arrivalTrack = document.getElementById('arrivalTrack');
  const leftArrow = document.querySelector('.left-arrow');
  const rightArrow = document.querySelector('.right-arrow');
  if (arrivalTrack && leftArrow && rightArrow) {
    leftArrow.addEventListener('click', () => arrivalTrack.scrollBy({ left: -300, behavior: 'smooth' }));
    rightArrow.addEventListener('click', () => arrivalTrack.scrollBy({ left: 300, behavior: 'smooth' }));
  }
}

// ===== New Arrivals Manual Scroll =====
function moveArrivalLeft() {
  document.getElementById("arrivalTrack").scrollBy({ left: -300, behavior: 'smooth' });
}
function moveArrivalRight() {
  document.getElementById("arrivalTrack").scrollBy({ left: 300, behavior: 'smooth' });
}

// ===== Product Page Quantity Counter =====
function decreaseQty() {
  const qty = document.getElementById('quantity');
  if (parseInt(qty.value) > 1) {
    qty.value--;
    document.getElementById('hiddenQuantity').value = qty.value;
  }
}

// ===== Shake Add to Cart Button =====
function shakeButton() {
  const button = document.getElementById('addToCartButton');
  if (button) {
    button.classList.add('shake');
    setTimeout(() => button.classList.remove('shake'), 400);
  }
}

// ===== Mobile Menu Toggle =====
function toggleMobileMenu() {
  document.getElementById("mobileMenu").classList.toggle("-translate-x-full");
}

// ===== Search Drawer Toggle =====
function toggleSearchDrawer() {
  document.getElementById("searchDrawer").classList.toggle("translate-x-full");
}

// ===== Instagram Section Carousel =====
let instaTrack = document.getElementById("instaTrack");
let instaScrollPosition = 0;

function moveInstaLeft() {
  const cardWidth = instaTrack.querySelector("a").offsetWidth;
  instaScrollPosition = Math.max(instaScrollPosition - cardWidth, 0);
  instaTrack.style.transform = `translateX(-${instaScrollPosition}px)`;
}
function moveInstaRight() {
  const cardWidth = instaTrack.querySelector("a").offsetWidth;
  const maxScroll = instaTrack.scrollWidth - instaTrack.clientWidth;
  instaScrollPosition = Math.min(instaScrollPosition + cardWidth, maxScroll);
  instaTrack.style.transform = `translateX(-${instaScrollPosition}px)`;
}

// ===== FAQ Toggle (Collapse Others) =====
function toggleFaq(element) {
  const item = element.parentElement;
  const isOpen = item.classList.contains("open");
  document.querySelectorAll('.faq-item').forEach(faq => {
    faq.classList.remove('open');
    faq.querySelector('.faq-icon').textContent = "+";
  });
  if (!isOpen) {
    item.classList.add("open");
    element.querySelector(".faq-icon").textContent = "-";
  }
}

// ===== Gallery Auto-Slider =====
let galleryIndex = 0;
function moveGallery() {
  const galleryTrack = document.getElementById('galleryTrack');
  const galleryImages = document.querySelectorAll('.gallery-image');
  if (galleryTrack && galleryImages.length > 0) {
    galleryIndex = (galleryIndex + 1) % galleryImages.length;
    galleryTrack.style.transform = `translateX(-${galleryIndex * 100}%)`;
  }
}

// ===== Wishlist Counter =====
function updateWishlistCount(count) {
  const badge = document.getElementById('wishlist-count');
  if (badge) badge.textContent = count;
}

// ===== Cart Panel Toggle + Refresh When Opening =====
function toggleCart() {
  const panel = document.getElementById('cartPanel');
  panel.classList.toggle('translate-x-full');
  if (!panel.classList.contains('translate-x-full')) refreshCart();
}

// ===== Add to Cart via AJAX =====
function addToCart(productId, quantity = 1) {
  fetch('/add-to-cart', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({ product_id: productId, quantity: quantity })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      document.getElementById('cartContent').innerHTML = data.cart_html;
      updateCartCount(data.total_quantity);
      updateCartSummary(data.subtotal);
      document.getElementById('cartPanel').classList.remove('translate-x-full');
    }
  })
  .catch(error => console.error('Error adding to cart:', error));
}


// ===== Update Cart Quantity via AJAX =====
function updateCartQuantity(productId, action) {
  fetch(`/update-cart/${productId}/${action}`, { method: 'POST' })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        document.getElementById('cartContent').innerHTML = data.cart_html;
        updateCartCount(data.total_quantity);
        updateCartSummary(data.subtotal);
      }
    })
    .catch(error => console.error('Error updating cart:', error));
}
function buyItNow(productId) {
  const quantity = parseInt(document.getElementById('quantity').value);

  fetch('/add-to-cart', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ product_id: productId, quantity: quantity })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      window.location.href = "/checkout";
    } else {
      alert("Failed to add product to cart.");
    }
  })
  .catch(err => console.error('Error:', err));
}


// ===== Update Cart Count Badge =====
function updateCartCount(count) {
  document.querySelectorAll('#cart-count, #cartCount').forEach(el => el.textContent = count);
}

// ===== Update Subtotal and Toggle Summary Section =====
function updateSubtotal(amount) {
  const summary = document.getElementById('cartSummary');
  const subtotalSpan = document.getElementById('cartSubtotal');
  if (summary && subtotalSpan) {
    if (amount > 0) {
      subtotalSpan.textContent = amount;
      summary.classList.remove('hidden');
    } else {
      summary.classList.add('hidden');
    }
  }
}

// ===== Refresh Full Cart Panel Content =====
function refreshCart() {
  fetch('/get-cart-data')
    .then(response => response.json())
    .then(data => {
      document.getElementById('cartContent').innerHTML = data.cart_html;
      updateCartCount(data.total_quantity);
      updateCartSummary(data.subtotal);
    })
    .catch(error => console.error('Error refreshing cart:', error));
}


// ===== Live Update Cart Badge On Page Load =====
function updateCartBadgeCount() {
  fetch('/get-cart-data')
    .then(response => response.json())
    .then(data => {
      updateCartCount(data.total_quantity);
    })
    .catch(error => console.error('Error fetching cart count:', error));
}
function updateCartSummary(subtotal) {
  const summary = document.getElementById('cartSummary');
  const subtotalSpan = document.getElementById('cartSubtotal');

  if (subtotal > 0) {
    subtotalSpan.textContent = `Rs. ${subtotal}`;
    summary.classList.remove('hidden');
  } else {
    summary.classList.add('hidden');
  }
}
function toggleReviewForm() {
  const form = document.getElementById('reviewForm');
  form.classList.toggle('hidden');
}
function deleteReview(productId, reviewId) {
  if (!confirm('Are you sure you want to delete this review?')) return;

  fetch(`/delete-review/${productId}/${reviewId}`, {
    method: 'POST'
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      fetch(`/get-reviews/${productId}`)
        .then(resp => resp.text())
        .then(html => {
          document.getElementById('reviewsContainer').innerHTML = html;
        });
    }
  })
  .catch(err => console.error('Error deleting review:', err));
}

