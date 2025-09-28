/**
 * Amazon-like cart controls: inline +/− quantity per product card and detail page.
 * Requires backend JSON endpoints:
 *  - GET  /api/carrito/estado
 *  - POST /api/carrito/agregar  { id: number, delta: +1|-1 }
 */
(function () {
  function qs(sel, root) { return (root || document).querySelector(sel); }
  function qsa(sel, root) { return Array.from((root || document).querySelectorAll(sel)); }

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

  async function changeQuantity(productId, delta) {
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
        // Show soft warning if stock reached
        console.info(data.mensaje);
      }
      // Update UI
      const qty = Number(data.cantidad || 0);
      toggleProductControls(productId, qty);
      setCartCount(Number(data.total_items || 0));
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
        if (pid) changeQuantity(pid, +1);
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