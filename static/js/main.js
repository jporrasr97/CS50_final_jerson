function toggleDescription(imgElement) {
    const productId = imgElement.getAttribute('data-product-id');
    const card = document.querySelector(`.product-card[data-product-id="${productId}"]`);

    if (card) {
        card.classList.toggle('expanded');
    }
}