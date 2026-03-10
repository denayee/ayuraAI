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
    let productsByStore = {"amazon": [], "flipkart": [], "nykaa": []};
    let currentFilter = "all";
    let currentOffset = 0;
    let currentQuery = "";
    let hasMore = false;
    let isLoading = false;
    let isExhausted = false;

    // Auto-fetch on page load
    function autoSearchProducts() {
        currentOffset = 0;
        allProducts = [];
        productsByStore = {"amazon": [], "flipkart": [], "nykaa": []};
        fetchTopRatedProducts();
    }

    // Fetch top-rated products from all stores
    function fetchTopRatedProducts() {
        if (isLoading) return;
        
        isLoading = true;
        
        if (currentOffset === 0) {
            // First load
            showElement(productsLoading);
            hideElement(productsEmpty);
            hideElement(searchQueryDisplay);
            hideElement(loadMoreContainer);
            hideElement(noMoreContainer);
            productsGrid.innerHTML = '';
        } else {
            // Load more
            showElement(productsLoading);
        }

        // Send request to backend
        fetch('/routes/api/fetch-products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                min_rating: 4.0,
                limit_per_store: 6,
                offset: currentOffset
            })
        })
        .then(response => response.json())
        .then(data => {
            isLoading = false;
            hideElement(productsLoading);

            if (data.success && data.products && data.products.length > 0) {
                if (currentOffset === 0) {
                    // First load - reset everything
                    allProducts = data.products;
                    productsByStore = data.by_store || {"amazon": [], "flipkart": [], "nykaa": []};
                    currentQuery = data.query;
                    productsGrid.innerHTML = '';
                } else {
                    // Load more - append to existing
                    allProducts = allProducts.concat(data.products);
                }
                
                hasMore = data.has_more || false;
                isExhausted = data.is_exhausted || false;
                
                // Update tab counts only on first load
                if (currentOffset === 0) {
                    updateTabCounts(data);
                    
                    // Display generated query
                    generatedQuery.textContent = data.query;
                    showElement(searchQueryDisplay);
                }

                // Display products for current filter
                displayProductsByFilter(currentFilter);
                
                // Update Load More button
                if (hasMore && !isExhausted) {
                    showElement(loadMoreContainer);
                    hideElement(noMoreContainer);
                } else if (isExhausted) {
                    hideElement(loadMoreContainer);
                    showElement(noMoreContainer);
                } else {
                    hideElement(loadMoreContainer);
                    showElement(noMoreContainer);
                }
            } else if (currentOffset === 0) {
                // No products on first load
                showElement(productsEmpty);
                hideElement(loadMoreContainer);
                hideElement(noMoreContainer);
            } else {
                // No more products on load more
                hideElement(loadMoreContainer);
                showElement(noMoreContainer);
                isExhausted = true;
            }
        })
        .catch(error => {
            console.error('Error fetching products:', error);
            isLoading = false;
            hideElement(productsLoading);
            if (currentOffset === 0) {
                showElement(productsEmpty);
            } else {
                hideElement(loadMoreContainer);
                showElement(noMoreContainer);
            }
        });
    }

    // Load more products
    function loadMoreProducts() {
        if (isLoading || !hasMore || isExhausted) return;
        currentOffset += 1;
        fetchTopRatedProducts();
    }

    // Update tab counts
    function updateTabCounts(data) {
        document.getElementById('all-count').textContent = data.total || 0;
        document.getElementById('amazon-count').textContent = data.amazon_count || 0;
        document.getElementById('flipkart-count').textContent = data.flipkart_count || 0;
        document.getElementById('nykaa-count').textContent = data.nykaa_count || 0;
    }

    // Display products filtered by store
    function displayProductsByFilter(filter) {
        // Build filtered products list
        let productsToDisplay = [];
        
        if (filter === "all") {
            productsToDisplay = allProducts;
        } else {
            // Filter by store from current all products
            productsToDisplay = allProducts.filter(p => p.store === filter);
        }

        if (productsToDisplay.length === 0 && currentOffset === 0) {
            showElement(productsEmpty);
            hideElement(loadMoreContainer);
            return;
        }

        // Add products to grid
        if (currentOffset === 0 || currentFilter !== filter) {
            // First load or filter changed
            productsGrid.innerHTML = '';
        }
        
        productsToDisplay.forEach((product, index) => {
            const productCard = createProductCard(product);
            productsGrid.appendChild(productCard);
        });

        showElement(productsGrid);
    }

    // Create individual product card
    function createProductCard(product) {
        const card = document.createElement('div');
        card.className = 'product-card-item';
        card.setAttribute('data-store', product.store);

        const storeColors = {
            'amazon': '#FF9900',
            'flipkart': '#1F5FE0',
            'nykaa': '#E91E63'
        };
        const storeColor = storeColors[product.store] || '#666';

        // Default image if not available
        const imageUrl = product.image || 'https://via.placeholder.com/200?text=No+Image';
        
        // Format price
        const price = product.price || 'Price N/A';
        const priceText = typeof price === 'number' ? `₹${price.toFixed(2)}` : price;

        // Build rating display
        const ratingHTML = product.rating 
            ? `<div class="product-rating">
                 <span class="stars">★</span>
                 <span class="rating-value">${product.rating}</span>
                 ${product.reviews ? `<span class="review-count">(${product.reviews})</span>` : ''}
               </div>`
            : '';

        const storeBadgeText = {
            'amazon': 'AMAZON',
            'flipkart': 'FLIPKART',
            'nykaa': 'NYKAA'
        }[product.store] || product.store.toUpperCase();

        card.innerHTML = `
            <div class="product-image-wrapper">
                <img src="${escapeHtml(imageUrl)}" alt="${escapeHtml(product.name)}" class="product-image" onerror="this.src='https://via.placeholder.com/200?text=Product+Image'">
                <span class="store-badge" style="background-color: ${storeColor}">${storeBadgeText}</span>
                <span class="rating-badge" title="Top Rated">⭐ TOP RATED</span>
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

    // Helper function to escape HTML
    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }

    // Helper functions to show/hide elements
    function showElement(el) {
        if (el) el.classList.remove('hidden-element');
    }

    function hideElement(el) {
        if (el) el.classList.add('hidden-element');
    }

    // Store tab click handlers
    storeTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Remove active class from all tabs
            storeTabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            
            // Update filter and display (don't need to load again, just filter)
            currentFilter = this.getAttribute('data-store');
            productsGrid.innerHTML = ''; // Clear grid
            displayProductsByFilter(currentFilter);
        });
    });

    // Load More button handler
    if (loadMoreBtn) {
        loadMoreBtn.addEventListener('click', loadMoreProducts);
    }

    // Auto-search on load
    setTimeout(autoSearchProducts, 500);

    // Update mobile view for products section
    const mobSelect = document.getElementById('mobile-section-select');
    if (mobSelect) {
        function updateMobileViewWithProducts() {
            if (window.innerWidth <= 768) {
                const activeClass = mobSelect.value;
                document.querySelectorAll('.recommendation-grid > div, .products-section').forEach(el => {
                    el.classList.remove('active-mob-card');
                    if (el.classList.contains(activeClass) || el.classList.contains('products-section') && activeClass === 'products-section') {
                        el.classList.add('active-mob-card');
                    }
                });
            }
        }

        mobSelect.addEventListener('change', updateMobileViewWithProducts);
        window.addEventListener('resize', updateMobileViewWithProducts);
    }
});
