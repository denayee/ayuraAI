// ==========================================
// static/js/ai_recommendation.js
// Markdown parsing, Avatars, Mobile Dropdown
// ==========================================

document.addEventListener('DOMContentLoaded', function() {
    const rawContent = document.getElementById('raw-content')?.textContent;
    const contentDiv = document.getElementById('ai-content');
    
    // Simple date string formatting
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    const dateEl = document.getElementById('current-date');
    if (dateEl) {
        dateEl.textContent = new Date().toLocaleDateString(undefined, options);
    }

    if (rawContent && rawContent.trim() !== 'None') {
        if (contentDiv && window.marked) {
            contentDiv.innerHTML = marked.parse(rawContent);
        }
    } else if (window.RecConfig?.profileIncomplete) {
        if (contentDiv) {
            contentDiv.innerHTML = "<p>No recommendation available. Please complete your profile or try again.</p>";
        }
    }

    // --- Mini Avatar on Recommendation Page ---
    const rGender = (window.RecConfig?.gender || "").toLowerCase().trim();
    const rMale = document.getElementById('rec-avatar-male');
    const rFemale = document.getElementById('rec-avatar-female');
    const rGeneric = document.getElementById('rec-avatar-generic');

    if (rGender === 'male') {
        if (rMale) rMale.style.display = 'block';
        if (rGeneric) rGeneric.style.display = 'none';
    } else if (rGender === 'female') {
        if (rFemale) rFemale.style.display = 'block';
        if (rGeneric) rGeneric.style.display = 'none';
    }

    // Apply stored skin color to the face
    const skinColorMap = { 'fair': '#F8D9C6', 'medium': '#E0AC84', 'olive': '#C68642', 'brown': '#8D5524', 'dark': '#3B2219' };
    const storedSkin = (window.RecConfig?.skinColor || "").toLowerCase();
    const skinHex = skinColorMap[storedSkin] || '#E0AC84';
    
    const faceEl = rGender === 'male' ? document.getElementById('rec-m-face') 
                 : (rGender === 'female' ? document.getElementById('rec-f-face') : null);
    
    if (faceEl) faceEl.style.fill = skinHex;

    // Apply stored hair color
    const hairColorMap = { 'black': '#090806', 'dark brown': '#3B3024', 'red': '#B55239', 'blonde': '#E6CEA8', 'light brown': '#A7856A', 'grey/white': '#E5E5E5' };
    const storedHair = (window.RecConfig?.hairColor || "").toLowerCase();
    const hairHex = hairColorMap[storedHair] || '#2C1E16';
    
    const hairEl = rGender === 'male' ? document.getElementById('rec-m-hair') 
                 : (rGender === 'female' ? document.getElementById('rec-f-hair') : null);
                 
    if (hairEl) hairEl.style.fill = hairHex;

    // --- Mobile Section Selector ---
    const mobSelect = document.getElementById('mobile-section-select');
    if (mobSelect) {
        function updateMobileView() {
            if (window.innerWidth <= 768) {
                const activeClass = mobSelect.value;
                // Hide all sections
                document.querySelectorAll('.recommendation-grid > div').forEach(el => {
                    el.classList.remove('active-mob-card');
                });
                const productsSection = document.querySelector('.products-section');
                if (productsSection) {
                    productsSection.classList.remove('active-mob-card');
                }
                
                // Show selected section
                if (activeClass === 'products-section') {
                    if (productsSection) {
                        productsSection.classList.add('active-mob-card');
                    }
                } else {
                    const activeElement = document.querySelector(`.${activeClass}`);
                    if (activeElement) {
                        activeElement.classList.add('active-mob-card');
                    }
                }
            } else {
                // Desktop: ensure all are visible via CSS
                document.querySelectorAll('.recommendation-grid > div').forEach(el => {
                    el.classList.remove('active-mob-card');
                });
                const productsSection = document.querySelector('.products-section');
                if (productsSection) {
                    productsSection.classList.remove('active-mob-card');
                }
            }
        }
        mobSelect.addEventListener('change', updateMobileView);
        window.addEventListener('resize', updateMobileView);
        updateMobileView(); // initialize
    }
});
