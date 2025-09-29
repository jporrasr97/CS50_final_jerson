/**
 * Amazon-like cart controls: inline +/− quantity per product card and detail page.
 * Requires backend JSON endpoints:
 *  - GET  /api/carrito/estado
 *  - POST /api/carrito/agregar  { id: number, delta: +1|-1 }
 */
(function () {
  function qs(sel, root) { return (root || document).querySelector(sel); }
  function qsa(sel, root) { return Array.from((root || document).querySelectorAll(sel)); }

  // Currency formatter for Guatemala Quetzal
  function formatCurrency(value) {
    const num = Number(value) || 0;
    try {
      return new Intl.NumberFormat('es-GT', {
        style: 'currency',
        currency: 'GTQ',
        maximumFractionDigits: 2
      }).format(num);
    } catch (e) {
      return 'Q' + num.toLocaleString('es-GT', { maximumFractionDigits: 2 });
    }
  }

  // Extract product info (image, name, price) near the clicked element
  function extractProductInfo(sourceEl) {
    const rootCard = sourceEl && sourceEl.closest('.product-card');
    let name = '';
    let price = 0;
    let imageUrl = '';

    // Try product list card first
    if (rootCard) {
      const nameEl = rootCard.querySelector('.card-title');
      if (nameEl) name = nameEl.getAttribute('title') || nameEl.textContent.trim();

      const priceEl = rootCard.querySelector('.h5.fw-bold, .text-primary.h5, .card .h5.fw-bold');
      if (priceEl) {
        const raw = priceEl.textContent.trim();
        const cleaned = raw.replace(/[^\d.,]/g, '').replace(/\./g, '').replace(',', '.');
        price = Number(cleaned) || 0;
      }

      const imgEl = rootCard.querySelector('img.product-image') || rootCard.querySelector('img');
      if (imgEl) imageUrl = imgEl.src;
    }

    // Fallbacks for detail page structure
    if (!name) {
      const detailName = qs('.product-details h2') || qs('.product-details .h3');
      if (detailName) name = detailName.textContent.trim();
    }
    if (!price) {
      const detailPrice = qs('.price-section .h2, .price-section .h3, .price-section [class*="h"]');
      if (detailPrice) {
        const raw = detailPrice.textContent.trim();
        const cleaned = raw.replace(/[^\d.,]/g, '').replace(/\./g, '').replace(',', '.');
        price = Number(cleaned) || 0;
      }
    }
    if (!imageUrl) {
      const detailImg = qs('.product-image-container img') || qs('img');
      if (detailImg) imageUrl = detailImg.src;
    }

    return { name, price, imageUrl };
  }

  // Show Bootstrap modal with confirmation UX
  function showAddedModal(info, subtotal) {
    try {
      const modalEl = document.getElementById('addedToCartModal');
      if (!modalEl) return;

      const img = modalEl.querySelector('#modal-product-image');
      const nameEl = modalEl.querySelector('#modal-product-name');
      const priceEl = modalEl.querySelector('#modal-product-price');
      const subtotalEl = modalEl.querySelector('#modal-cart-subtotal');

      if (img && info.imageUrl) img.src = info.imageUrl;
      if (nameEl) nameEl.textContent = info.name || 'Producto';
      if (priceEl) priceEl.textContent = formatCurrency(info.price);
      if (subtotalEl) subtotalEl.textContent = formatCurrency(subtotal);

      const ModalCtor = window.bootstrap && window.bootstrap.Modal ? window.bootstrap.Modal : null;
      if (ModalCtor) {
        const modal = new ModalCtor(modalEl);
        modal.show();
      }
    } catch (e) {
      // swallow errors to avoid blocking UX
    }
  }

  function setCartCount(count) {
    const badge = qs('#cart-count');
    if (!badge) return;
    const num = Number(count) || 0;
    badge.textContent = String(num);
    badge.style.display = num > 0 ? 'inline-flex' : 'none';
  }

  function toggleProductControls(productId, quantity) {
    const addBtn = qs(`.btn-add-to-cart[data-product-id="${productId}"]`);
    const qtyBox = qs(`.amazon-qty[data-product-id="${productId}"]`);
    const qtyCount = qs(`.amazon-qty[data-product-id="${productId}"] .qty-count`);
    if (!qtyBox) return;

    const q = Math.max(0, Number(quantity) || 0);
    if (qtyCount) qtyCount.textContent = String(q);

    if (q > 0) {
      qtyBox.classList.remove('d-none');
      if (addBtn) addBtn.classList.add('d-none');
    } else {
      qtyBox.classList.add('d-none');
      if (addBtn) addBtn.classList.remove('d-none');
    }
  }

  async function fetchCartState() {
    try {
      const res = await fetch('/api/carrito/estado', { credentials: 'same-origin' });
      if (!res.ok) return;
      const data = await res.json();
      if (!data || !data.ok) return;
      // Update badge
      setCartCount(data.total_items || 0);
      // Update all products present in the DOM
      qsa('.amazon-qty').forEach(el => {
        const pid = Number(el.getAttribute('data-product-id'));
        const qty = Number((data.items && data.items[String(pid)]) || 0);
        toggleProductControls(pid, qty);
      });
    } catch (e) {
      // ignore network errors silently for UX
    }
  }

  async function changeQuantity(productId, delta, opts) {
    opts = opts || {};
    try {
      const res = await fetch('/api/carrito/agregar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'same-origin',
        body: JSON.stringify({ id: productId, delta: delta })
      });
      const data = await res.json();
      if (!res.ok) {
        alert(data && data.mensaje ? data.mensaje : 'Error actualizando el carrito');
        return;
      }
      if (data.mensaje) {
        // Show soft warning if stock reached or other info
        console.info(data.mensaje);
      }
      // Update UI
      const qty = Number(data.cantidad || 0);
      toggleProductControls(productId, qty);
      setCartCount(Number(data.total_items || 0));

      // If this came from the main "Agregar al Carrito" button and operation succeeded, show modal
      if (opts.showModal && delta > 0 && data && data.ok !== false) {
        const info = extractProductInfo(opts.sourceEl || document.body);
        const subtotal = typeof data.total !== 'undefined' ? data.total : 0;
        showAddedModal(info, subtotal);
      }
    } catch (e) {
      alert('No se pudo actualizar el carrito. Revisa tu conexión.');
    }
  }

  function bindEvents() {
    // Add to cart buttons
    document.addEventListener('click', function (ev) {
      const addBtn = ev.target.closest('.btn-add-to-cart');
      if (addBtn) {
        ev.preventDefault();
        const pid = Number(addBtn.getAttribute('data-product-id'));
        if (pid) changeQuantity(pid, +1, { sourceEl: addBtn, showModal: true });
      }

      const minusBtn = ev.target.closest('.qty-minus');
      if (minusBtn) {
        ev.preventDefault();
        const box = minusBtn.closest('.amazon-qty');
        const pid = Number(box && box.getAttribute('data-product-id'));
        if (pid) changeQuantity(pid, -1);
      }

      const plusBtn = ev.target.closest('.qty-plus');
      if (plusBtn) {
        ev.preventDefault();
        const box = plusBtn.closest('.amazon-qty');
        const pid = Number(box && box.getAttribute('data-product-id'));
        if (pid) changeQuantity(pid, +1);
      }
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    bindEvents();
    fetchCartState();
  });
})();