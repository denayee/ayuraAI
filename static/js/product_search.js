// ==========================================
// static/js/product_search.js
// Handle top-rated product search with pagination
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    const storeTabs = document.querySelectorAll('.store-tab');
    const productsGrid = document.getElementById('products-grid');
    const productsLoading = document.getElementById('products-loading');
    const productsEmpty = document.getElementById('products-empty');
    const searchQueryDisplay = document.getElementById('search-query-display');
    const generatedQuery = document.getElementById('generated-query');
    const loadMoreBtn = document.getElementById('load-more-btn');
    const loadMoreContainer = document.getElementById('load-more-container');
    const noMoreContainer = document.getElementById('no-more-container');

    let allProducts = [];
    let currentFilter = 'all';
    let currentOffset = 0;
    let isLoading = false;
    let hasMore = true;
    let isExhausted = false;
    let hasError = false;

    function resetSearchState() {
        allProducts = [];
        currentOffset = 0;
        isLoading = false;
        hasMore = true;
        isExhausted = false;
        hasError = false;
    }

    function autoSearchProducts() {
        resetSearchState();
        fetchTopRatedProducts();
    }

    async function fetchTopRatedProducts() {
        if (isLoading) return;

        isLoading = true;
        hasError = false;

        showElement(productsLoading);
        if (currentOffset === 0) {
            hideElement(productsEmpty);
            hideElement(searchQueryDisplay);
            productsGrid.innerHTML = '';
        }
        hideElement(loadMoreContainer);
        hideElement(noMoreContainer);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 65000);

        try {
            const { response, result } = await window.AyuraApi.jsonRequest('/routes/api/fetch-products', {
                method: 'POST',
                data: {
                    min_rating: 4.0,
                    offset: currentOffset,
                },
                signal: controller.signal,
            });

            clearTimeout(timeoutId);
            isLoading = false;
            hideElement(productsLoading);

            if (response.ok && result.success && Array.isArray(result.products) && result.products.length > 0) {
                if (currentOffset === 0) {
                    allProducts = result.products;
                    productsGrid.innerHTML = '';
                } else {
                    const existingIds = new Set(allProducts.map(product => product.link));
                    const newProducts = result.products.filter(product => !existingIds.has(product.link));
                    allProducts = allProducts.concat(newProducts);
                }

                hasMore = result.has_more;
                isExhausted = result.is_exhausted;

                updateTabCounts(result);
                generatedQuery.textContent = result.query || '';
                showElement(searchQueryDisplay);
                displayProductsByFilter(currentFilter);
                updateLoadMoreVisibility();
                return;
            }

            if (currentOffset === 0) {
                showElement(productsEmpty);
                const emptyMsg = productsEmpty.querySelector('p');
                if (emptyMsg) {
                    emptyMsg.textContent = 'No top-rated products found for this profile. Try adjusting your settings.';
                }
            }

            hasMore = false;
            isExhausted = true;
            hideElement(productsLoading);
            updateLoadMoreVisibility();
        } catch (error) {
            clearTimeout(timeoutId);
            console.error('Error fetching products:', error);
            isLoading = false;
            hideElement(productsLoading);
            hasError = true;

            if (allProducts.length === 0) {
                const emptyMsg = productsEmpty.querySelector('p');
                if (emptyMsg) {
                    emptyMsg.textContent = error.name === 'AbortError'
                        ? 'Request timed out. Click below to retry.'
                        : 'Unable to load products right now. Click below to retry.';
                }
                showElement(productsEmpty);

                const btnText = loadMoreBtn.querySelector('.load-more-text') || loadMoreBtn;
                btnText.textContent = 'Try Again';
                showElement(loadMoreContainer);
            }
        }
    }

    function updateLoadMoreVisibility() {
        const btnText = loadMoreBtn.querySelector('.load-more-text');
        if (btnText) {
            btnText.textContent = 'Load More Products';
        }

        if (isLoading) {
            hideElement(loadMoreContainer);
            hideElement(noMoreContainer);
            return;
        }

        if (hasMore && !isExhausted) {
            showElement(loadMoreContainer);
            hideElement(noMoreContainer);
        } else if (isExhausted || !hasMore) {
            hideElement(loadMoreContainer);
            showElement(noMoreContainer);
        } else {
            hideElement(loadMoreContainer);
            hideElement(noMoreContainer);
        }
    }

    function loadMoreProducts() {
        if (isLoading) return;

        if (!hasError) {
            currentOffset += 1;
        }

        fetchTopRatedProducts();
    }

    function updateTabCounts(data) {
        document.getElementById('all-count').textContent = data.total || 0;
        document.getElementById('amazon-count').textContent = data.amazon_count || 0;
        document.getElementById('flipkart-count').textContent = data.flipkart_count || 0;
        document.getElementById('nykaa-count').textContent = data.nykaa_count || 0;

        storeTabs.forEach(tab => {
            const tabStore = tab.getAttribute('data-store');

            if (tabStore === 'amazon' && (!data.amazon_count || data.amazon_count === 0)) {
                hideElement(tab);
            } else if (tabStore === 'flipkart' && (!data.flipkart_count || data.flipkart_count === 0)) {
                hideElement(tab);
            } else if (tabStore === 'nykaa' && (!data.nykaa_count || data.nykaa_count === 0)) {
                hideElement(tab);
            } else {
                showElement(tab);
            }
        });

        const activeTab = Array.from(storeTabs).find(tab => tab.classList.contains('active'));
        if (activeTab && activeTab.classList.contains('hidden-element')) {
            const allTab = Array.from(storeTabs).find(tab => tab.getAttribute('data-store') === 'all');
            if (allTab) {
                allTab.click();
            }
        }
    }

    function displayProductsByFilter(filter) {
        let productsToDisplay = [];

        if (filter === 'all') {
            productsToDisplay = allProducts;
        } else {
            productsToDisplay = allProducts.filter(product => product.store === filter);
        }

        if (productsToDisplay.length === 0) {
            const emptyMsg = productsEmpty.querySelector('p');
            if (emptyMsg) {
                emptyMsg.textContent = `No ${filter !== 'all' ? filter : ''} products found.`;
            }
            showElement(productsEmpty);
            hideElement(productsLoading);
            return;
        }

        hideElement(productsEmpty);

        if (currentOffset === 0 || currentFilter !== filter) {
            productsGrid.innerHTML = '';
        }

        productsToDisplay.forEach(product => {
            const productCard = createProductCard(product);
            productsGrid.appendChild(productCard);
        });

        showElement(productsGrid);
    }

    function createProductCard(product) {
        const card = document.createElement('div');
        card.className = 'product-card-item';
        card.setAttribute('data-store', product.store);

        const storeColors = {
            amazon: '#FF9900',
            flipkart: '#1F5FE0',
            nykaa: '#E91E63',
        };
        const storeColor = storeColors[product.store] || '#666';
        const imageUrl = product.image || 'https://via.placeholder.com/200?text=No+Image';
        const price = product.price || 'Price N/A';
        const priceText = typeof price === 'number' ? `Rs.${price.toFixed(2)}` : price;

        const ratingHTML = product.rating
            ? `<div class="product-rating">
                 <span class="stars">★</span>
                 <span class="rating-value">${product.rating}</span>
                 ${product.reviews ? `<span class="review-count">(${product.reviews})</span>` : ''}
               </div>`
            : '';

        const storeBadgeText = {
            amazon: 'AMAZON',
            flipkart: 'FLIPKART',
            nykaa: 'NYKAA',
        }[product.store] || product.store.toUpperCase();

        card.innerHTML = `
            <div class="product-image-wrapper">
                <img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(product.name)}" class="product-image" onerror="this.src='https://via.placeholder.com/200?text=Product+Image'">
                <span class="store-badge" style="background-color: ${storeColor}">${storeBadgeText}</span>
                <span class="rating-badge" title="Top Rated">TOP RATED</span>
            </div>
            <div class="product-info">
                <h4 class="product-name">${escapeHtml(product.name)}</h4>
                <div class="product-meta">
                    <span class="product-price">${escapeHtml(priceText)}</span>
                    ${ratingHTML}
                </div>
                <div class="product-source">From ${escapeHtml(product.source)}</div>
            </div>
            <a href="${escapeHtml(product.link)}" target="_blank" rel="noopener noreferrer" class="product-link-btn">
                View on ${storeBadgeText}
            </a>
        `;

        return card;
    }

    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;',
        };
        return String(text).replace(/[&<>"']/g, character => map[character]);
    }

    function showElement(element) {
        if (element) element.classList.remove('hidden-element');
    }

    function hideElement(element) {
        if (element) element.classList.add('hidden-element');
    }

    storeTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            storeTabs.forEach(storeTab => storeTab.classList.remove('active'));
            this.classList.add('active');

            currentFilter = this.getAttribute('data-store');
            productsGrid.innerHTML = '';
            displayProductsByFilter(currentFilter);
            updateLoadMoreVisibility();
        });
    });

    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreProducts);
    }

    setTimeout(autoSearchProducts, 500);

    const mobSelect = document.getElementById('mobile-section-select');
    if (mobSelect) {
        function updateMobileViewWithProducts() {
            if (window.innerWidth <= 768) {
                const activeClass = mobSelect.value;
                document.querySelectorAll('.recommendation-grid > div, .products-section').forEach(element => {
                    element.classList.remove('active-mob-card');
                    if (
                        element.classList.contains(activeClass) ||
                        (element.classList.contains('products-section') && activeClass === 'products-section')
                    ) {
                        element.classList.add('active-mob-card');
                    }
                });
            }
        }

        mobSelect.addEventListener('change', updateMobileViewWithProducts);
        window.addEventListener('resize', updateMobileViewWithProducts);
    }
});
