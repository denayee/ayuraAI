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
    let currentQuery = "";
    let currentOffset = 0;
    let isLoading = false;
    let hasMore = true;
    let isExhausted = false;
    let hasError = false;

    // Auto-fetch on page load
    function autoSearchProducts() {
        allProducts = [];
        productsByStore = {"amazon": [], "flipkart": [], "nykaa": []};
        currentOffset = 0;
        isLoading = false;
        hasMore = true;
        isExhausted = false;
        hasError = false;
        fetchTopRatedProducts();
    }

    // Fetch top-rated products from all stores
    function fetchTopRatedProducts() {
        if (isLoading) return;

        isLoading = true;
        hasError = false;

        // Reset UI for load
        showElement(productsLoading);
        if (currentOffset === 0) {
            hideElement(productsEmpty);
            hideElement(searchQueryDisplay);
            productsGrid.innerHTML = '';
        }
        hideElement(loadMoreContainer);
        hideElement(noMoreContainer);

        // Send request to backend with timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 65000); // 65 second timeout (matches backend)

        fetch('/routes/api/fetch-products', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                min_rating: 4.0,
                offset: currentOffset
            }),
            signal: controller.signal
        })
        .then(response => response.json())
        .then(data => {
            clearTimeout(timeoutId);
            isLoading = false;
            hideElement(productsLoading);

            if (data.success && data.products && data.products.length > 0) {
                if (currentOffset === 0) {
                    allProducts = data.products;
                    productsByStore = data.by_store || {"amazon": [], "flipkart": [], "nykaa": []};
                    productsGrid.innerHTML = '';
                } else {
                    const existingIds = new Set(allProducts.map(p => p.link));
                    const newProducts = data.products.filter(p => !existingIds.has(p.link));
                    allProducts = allProducts.concat(newProducts);
                }

                currentQuery = data.query;
                hasMore = data.has_more;
                isExhausted = data.is_exhausted;

                // Update tab counts
                updateTabCounts(data);

                // Display generated query
                generatedQuery.textContent = data.query;
                showElement(searchQueryDisplay);

                // Display products for current filter
                displayProductsByFilter(currentFilter);
                updateLoadMoreVisibility();
            } else if (currentOffset === 0) {
                // No products strictly on first load
                showElement(productsEmpty);
                const emptyMsg = productsEmpty.querySelector('p');
                if (emptyMsg) {
                    emptyMsg.textContent = 'No top-rated products found for this profile. Try adjusting your settings.';
                }
                hasMore = false;
                isExhausted = true;
                hideElement(productsLoading);
                updateLoadMoreVisibility();
            } else {
                // Exhausted subsequent load
                hasMore = false;
                isExhausted = true;
                hideElement(productsLoading);
                updateLoadMoreVisibility();
            }
        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('Error fetching products:', error);
            isLoading = false;
            hideElement(productsLoading); // Ensure loading is hidden on error
            hasError = true;

            // Check if it was a timeout error
            if (error.name === 'AbortError') {
                console.error('Request timed out');
            }

            // Show retry button instead of giving up
            if (allProducts.length === 0) {
                // No products loaded yet - show retry button
                const emptyMsg = productsEmpty.querySelector('p');
                if (emptyMsg) {
                    emptyMsg.textContent = '⏱️ Request timed out. Click below to retry.';
                }
                showElement(productsEmpty);
                
                // Keep the button available for Retry
                const btnText = loadMoreBtn.querySelector('.load-more-text') || loadMoreBtn;
                btnText.textContent = '🔄 Try Again';
                showElement(loadMoreContainer);
            }
        });
    }

    // Update Load More button visibility based on state
    function updateLoadMoreVisibility() {
        const btnText = loadMoreBtn.querySelector('.load-more-text');
        if (btnText) {
            btnText.textContent = '📦 Load More Products';
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

    // Load more products
    function loadMoreProducts() {
        if (isLoading) return;
        
        if (!hasError) {
            currentOffset += 1;
        }

        console.log('Loading more products at offset:', currentOffset);
        fetchTopRatedProducts();
    }

    // Update tab counts
    function updateTabCounts(data) {
        document.getElementById('all-count').textContent = data.total || 0;
        document.getElementById('amazon-count').textContent = data.amazon_count || 0;
        document.getElementById('flipkart-count').textContent = data.flipkart_count || 0;
        document.getElementById('nykaa-count').textContent = data.nykaa_count || 0;
        
        // Hide tabs that returned exactly 0 products
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
        
        // If the current tab went empty, default back to 'all'
        const activeTab = Array.from(storeTabs).find(tab => tab.classList.contains('active'));
        if (activeTab && activeTab.classList.contains('hidden-element')) {
            // Find the 'All' tab and click it to reset the view gracefully
            const allTab = Array.from(storeTabs).find(tab => tab.getAttribute('data-store') === 'all');
            if (allTab) {
                allTab.click();
            }
        }
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

        if (productsToDisplay.length === 0) {
            const emptyMsg = productsEmpty.querySelector('p');
            if (emptyMsg) {
                emptyMsg.textContent = `No ${filter !== 'all' ? filter : ''} products found.`;
            }
            hideElement(productsLoading); // Guarantee spinner is hidden if empty
            return;
        } else {
            hideElement(productsEmpty);
        }

        // Add products to grid
        if (currentOffset === 0 || currentFilter !== filter) {
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
            
            currentFilter = this.getAttribute('data-store');
            productsGrid.innerHTML = ''; // Clear grid
            displayProductsByFilter(currentFilter);
            updateLoadMoreVisibility();
        });
    });

    // Load More button handler is now back to pagination!
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
