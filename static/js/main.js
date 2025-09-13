function toggleDescription(imgElement) {
    const productId = imgElement.getAttribute('data-product-id');
    const description = document.querySelector(`.product-description[data-product-id="${productId}"]`);

    if (description) {
        description.classList.toggle('expanded');
    }
}