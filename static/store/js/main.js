/* ============================================================
   ShopZen — Main JavaScript
   ============================================================ */

// ── Navbar Scroll Effect ─────────────────────────────────────
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 20);
}, { passive: true });

// ── Hamburger / Mobile Menu ──────────────────────────────────
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobile-menu');
if (hamburger && mobileMenu) {
  hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('open');
    mobileMenu.classList.toggle('show');
  });
}

// ── User Dropdown ────────────────────────────────────────────
const userMenuBtn = document.getElementById('user-menu-btn');
const userDropdown = document.getElementById('user-dropdown');
if (userMenuBtn && userDropdown) {
  userMenuBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    userMenuBtn.classList.toggle('open');
    userDropdown.classList.toggle('show');
  });
  document.addEventListener('click', (e) => {
    if (!userMenuBtn.contains(e.target)) {
      userMenuBtn.classList.remove('open');
      userDropdown.classList.remove('show');
    }
  });
}

// ── Toast Notifications ──────────────────────────────────────
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', info: 'fa-info-circle', warning: 'fa-exclamation-triangle' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('fade-out');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ── Cart Badge Update ────────────────────────────────────────
function updateCartBadge(count) {
  const badge = document.getElementById('cart-badge');
  if (badge) {
    badge.textContent = count;
    badge.classList.add('bump');
    setTimeout(() => badge.classList.remove('bump'), 300);
  }
}

// ── AJAX Helper ──────────────────────────────────────────────
async function apiPost(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': CSRF_TOKEN,
    },
    body: JSON.stringify(data),
  });
  return res.json();
}

// ── Add to Cart ──────────────────────────────────────────────
async function addToCart(productId, quantity = 1, btn = null) {
  if (btn) {
    btn.classList.add('loading');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
  }
  try {
    const data = await apiPost(URLS.addToCart, { product_id: productId, quantity });
    if (data.success) {
      updateCartBadge(data.cart_count);
      showToast(data.message || 'Added to cart!', 'success');
      if (btn) {
        btn.innerHTML = '<i class="fas fa-check"></i> Added!';
        btn.classList.remove('loading');
        btn.classList.add('added');
        setTimeout(() => {
          btn.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
          btn.classList.remove('added');
        }, 2000);
      }
    } else {
      showToast(data.message || 'Failed to add to cart.', 'error');
      if (btn) {
        btn.classList.remove('loading');
        btn.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
      }
    }
  } catch (err) {
    showToast('Network error. Please try again.', 'error');
    if (btn) {
      btn.classList.remove('loading');
      btn.innerHTML = '<i class="fas fa-cart-plus"></i> Add to Cart';
    }
  }
}

// ── Update Cart Item ─────────────────────────────────────────
async function updateCartItem(itemId, newQty) {
  try {
    const data = await apiPost(URLS.updateCart, { item_id: itemId, quantity: newQty });
    if (data.success) {
      updateCartBadge(data.cart_count);
      if (newQty < 1) {
        // Remove the row
        const row = document.getElementById(`cart-item-${itemId}`);
        if (row) {
          row.style.opacity = '0';
          row.style.transform = 'translateX(-20px)';
          row.style.transition = 'all 0.3s ease';
          setTimeout(() => { row.remove(); checkEmptyCart(); }, 300);
        }
      } else {
        // Update display
        const qtyEl = document.getElementById(`qty-${itemId}`);
        const subtotalEl = document.getElementById(`subtotal-${itemId}`);
        if (qtyEl) qtyEl.textContent = newQty;
        if (subtotalEl) subtotalEl.textContent = `$${data.item_subtotal}`;
        // Update totals
        updateCartTotals(data.cart_total, data.cart_count);
      }
    }
  } catch (err) {
    showToast('Failed to update cart.', 'error');
  }
}

// ── Remove Cart Item ─────────────────────────────────────────
async function removeCartItem(itemId) {
  try {
    const data = await apiPost(URLS.removeFromCart, { item_id: itemId });
    if (data.success) {
      updateCartBadge(data.cart_count);
      const row = document.getElementById(`cart-item-${itemId}`);
      if (row) {
        row.style.opacity = '0';
        row.style.transform = 'translateX(-20px)';
        row.style.transition = 'all 0.3s ease';
        setTimeout(() => { row.remove(); checkEmptyCart(); }, 300);
      }
      updateCartTotals(data.cart_total, data.cart_count);
      showToast('Item removed from cart.', 'info');
    }
  } catch (err) {
    showToast('Failed to remove item.', 'error');
  }
}

function updateCartTotals(total, count) {
  const subtotalEl = document.getElementById('cart-subtotal');
  const totalEl = document.getElementById('cart-total');
  const countEl = document.getElementById('total-count');
  if (subtotalEl) subtotalEl.textContent = `$${total}`;
  if (totalEl) totalEl.textContent = `$${total}`;
  if (countEl) countEl.textContent = count;
}

function checkEmptyCart() {
  const items = document.querySelectorAll('.cart-item');
  if (items.length === 0) {
    location.reload();
  }
}

// ── Product List View Toggle ─────────────────────────────────
function setView(mode) {
  const container = document.getElementById('products-container');
  const gridBtn = document.getElementById('grid-view');
  const listBtn = document.getElementById('list-view');
  if (!container) return;

  if (mode === 'list') {
    container.classList.add('list-mode');
    listBtn.classList.add('active');
    gridBtn.classList.remove('active');
  } else {
    container.classList.remove('list-mode');
    gridBtn.classList.add('active');
    listBtn.classList.remove('active');
  }
  localStorage.setItem('shopzen-view', mode);
}

// Restore view preference
const savedView = localStorage.getItem('shopzen-view');
if (savedView === 'list') setView('list');

// ── Sidebar Toggle (mobile) ──────────────────────────────────
function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  if (sidebar) sidebar.classList.toggle('show');
}

// ── Payment Option Toggle ────────────────────────────────────
document.querySelectorAll('.payment-option').forEach(opt => {
  opt.addEventListener('click', () => {
    document.querySelectorAll('.payment-option').forEach(o => o.classList.remove('active'));
    opt.classList.add('active');
  });
});

// ── Password Toggle ──────────────────────────────────────────
function togglePassword(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  const isText = input.type === 'text';
  input.type = isText ? 'password' : 'text';
  btn.innerHTML = isText ? '<i class="fas fa-eye"></i>' : '<i class="fas fa-eye-slash"></i>';
}

// ── Auto-dismiss Django messages ─────────────────────────────
document.querySelectorAll('.alert').forEach(alert => {
  setTimeout(() => {
    alert.style.opacity = '0';
    alert.style.transform = 'translateY(-10px)';
    alert.style.transition = 'all 0.4s ease';
    setTimeout(() => alert.remove(), 400);
  }, 4000);
});

// ── Hero Particle Animation ──────────────────────────────────
const particleCanvas = document.getElementById('particles');
if (particleCanvas) {
  const canvas = document.createElement('canvas');
  canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;';
  particleCanvas.appendChild(canvas);
  const ctx = canvas.getContext('2d');

  function resizeCanvas() {
    canvas.width = particleCanvas.offsetWidth;
    canvas.height = particleCanvas.offsetHeight;
  }
  resizeCanvas();
  window.addEventListener('resize', resizeCanvas, { passive: true });

  const particles = Array.from({ length: 60 }, () => ({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: Math.random() * 2 + 0.5,
    dx: (Math.random() - 0.5) * 0.4,
    dy: (Math.random() - 0.5) * 0.4,
    alpha: Math.random() * 0.5 + 0.1,
  }));

  function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(157, 106, 255, ${p.alpha})`;
      ctx.fill();
      p.x += p.dx;
      p.y += p.dy;
      if (p.x < 0 || p.x > canvas.width) p.dx *= -1;
      if (p.y < 0 || p.y > canvas.height) p.dy *= -1;
    });
    requestAnimationFrame(animateParticles);
  }
  animateParticles();
}

// ── Input Focus Enhancement ──────────────────────────────────
document.querySelectorAll('.form-control').forEach(input => {
  input.addEventListener('focus', () => {
    input.closest('.form-group')?.classList.add('focused');
  });
  input.addEventListener('blur', () => {
    input.closest('.form-group')?.classList.remove('focused');
  });
});
