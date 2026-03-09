document.addEventListener('DOMContentLoaded', function() {
    // Initial check
    handleSkinType();
    handleScalpCondition();
});

function toggleField(elementId, show) {
    const el = document.getElementById(elementId);
    if (!el) return;
    
    if (show) {
        el.classList.remove('hidden');
        const input = el.querySelector('input');
        if (input) input.setAttribute('required', 'required'); 
    } else {
        el.classList.add('hidden');
        const input = el.querySelector('input');
        if (input) {
            input.removeAttribute('required');
            input.value = ''; // Clean up
        }
    }
}

function handleSkinType() {
    const skinType = document.querySelector('select[name="skin_type"]')?.value;
    if (!skinType) return;

    const oilGroup = document.getElementById('skin-oil-group');
    const drynessGroup = document.getElementById('dryness-group'); // Container for presence+level
    const drynessPresenceYes = document.querySelector('input[name="dryness_presence"][value="Yes"]');
    const drynessPresenceNo = document.querySelector('input[name="dryness_presence"][value="No"]');
    
    // Logic: Oily -> Show Oil Level
    if (skinType === 'Oily') {
        if(oilGroup) toggleField('skin-oil-group', true);
    } else {
        if(oilGroup) toggleField('skin-oil-group', false);
    }

    // Logic: Dry -> Show Dryness Level (Auto-select Yes)
    if (skinType === 'Dry') {
         // Auto-set presence to Yes and show level
         if(drynessPresenceYes) drynessPresenceYes.click();
    } else {
        if(drynessPresenceNo && skinType !== '') drynessPresenceNo.click();
    }
}

function handleScalpCondition() {
    const conditionEl = document.querySelector('select[name="scalp_condition"]');
    if (!conditionEl) return;
    const condition = conditionEl.value;
    const hairDrynessPresenceYes = document.querySelector('input[name="hair_dryness_presence"][value="Yes"]');
    const hairDrynessPresenceNo = document.querySelector('input[name="hair_dryness_presence"][value="No"]');

    // If Scalp is Dry -> Auto-trigger Hair Dryness logic
    if (condition === 'Dry') {
        if(hairDrynessPresenceYes) hairDrynessPresenceYes.click();
    } else {
         if(hairDrynessPresenceNo && condition !== '') hairDrynessPresenceNo.click();
    }
}

// --- 3-Step Navigation Logic ---
let currentStep = 1;
const totalSteps = 3;

function updateProgress() {
    const stepText = document.getElementById('step-text');
    const progressFill = document.getElementById('progress-fill');
    if (stepText) stepText.innerText = `Step ${currentStep} of ${totalSteps}`;
    if (progressFill) {
        const progressPercent = ((currentStep - 1) / (totalSteps - 1)) * 100;
        progressFill.style.width = `${progressPercent}%`;
    }
}

function showStep(step) {
    // Hide all
    document.querySelectorAll('.form-step').forEach(el => {
        el.classList.remove('active');
        el.style.display = 'none';
    });
    
    // Show target
    const target = document.getElementById(`step-${step}`);
    if (!target) return;
    
    target.style.display = 'block';
    // Trigger reflow for animation
    void target.offsetWidth;
    target.classList.add('active');
    
    currentStep = step;
    updateProgress();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Global scope for onclick="nextStep(x)"
window.nextStep = function(step) {
    const currentContainer = document.getElementById(`step-${currentStep}`);
    if (!currentContainer) return;

    // Very basic validation - check if required fields in current step are filled
    const requiredInputs = currentContainer.querySelectorAll('input[required], select[required]');
    let allValid = true;
    
    requiredInputs.forEach(input => {
        if (!input.value || (input.type === 'radio' && !currentContainer.querySelector(`input[name="${input.name}"]:checked`))) {
            allValid = false;
            input.reportValidity(); // Show native browser warning
        }
    });

    if (allValid) {
        showStep(step);
    }
};

window.toggleField = toggleField;
window.handleSkinType = handleSkinType;
window.handleScalpCondition = handleScalpCondition;
window.showStep = showStep;

// Add selected highlight to dropdowns
document.querySelectorAll('select').forEach(sel => {
    sel.addEventListener('change', function() {
        if(this.value && this.value !== "") {
            this.classList.add('has-val');
        } else {
            this.classList.remove('has-val');
        }
    });
});

// --- Gender-Aware Live Avatar Binding ---
document.addEventListener('DOMContentLoaded', function initAvatar() {
    const userGender = (window.AppConfig?.gender || "").toLowerCase().trim();
    const maleAvatar = document.getElementById('avatar-male');
    const femaleAvatar = document.getElementById('avatar-female');
    const genericAvatar = document.getElementById('avatar-generic');
    const genderBadge = document.getElementById('gender-badge');

    if (userGender === 'male') {
        if (maleAvatar) maleAvatar.style.display = 'block';
        if (genericAvatar) genericAvatar.style.display = 'none';
        if (genderBadge) genderBadge.textContent = '♂ Male';
    } else if (userGender === 'female') {
        if (femaleAvatar) femaleAvatar.style.display = 'block';
        if (genericAvatar) genericAvatar.style.display = 'none';
        if (genderBadge) genderBadge.textContent = '♀ Female';
    }

    function getAvatarPaths() {
        if (userGender === 'male') return { face: document.getElementById('m-face'), hairBg: document.getElementById('m-hair-bg'), hairFront: document.getElementById('m-hair-front') };
        if (userGender === 'female') return { face: document.getElementById('f-face'), hairBg: document.getElementById('f-hair-bg'), hairFront: document.getElementById('f-hair-front') };
        return { face: document.getElementById('avatar-face'), hairBg: document.getElementById('avatar-hair-bg'), hairFront: document.getElementById('avatar-hair-front') };
    }

    const hairShapeMap = {
        male: {
            "Straight": { bg: "M100,15 C150,15 188,45 188,100 C188,115 184,130 178,145 L172,145 C172,100 155,50 100,50 C45,50 28,100 28,145 L22,145 C16,130 12,115 12,100 C12,45 50,15 100,15 Z", front: "M100,20 C140,20 160,40 170,80 C145,55 120,55 100,60 C80,55 55,55 30,80 C40,40 60,20 100,20 Z" },
            "Wavy": { bg: "M100,12 C155,12 195,48 195,108 C195,125 190,138 183,150 L176,148 C174,105 158,52 100,52 C42,52 26,105 24,148 L17,150 C10,138 5,125 5,108 C5,48 45,12 100,12 Z", front: "M100,20 C140,20 160,40 170,80 C145,55 120,55 100,60 C80,55 55,55 30,80 C40,40 60,20 100,20 Z" },
            "Curly": { bg: "M100,8 C158,8 198,50 198,110 C198,128 193,142 185,155 L178,152 C175,108 158,50 100,50 C42,50 25,108 22,152 L15,155 C7,142 2,128 2,110 C2,50 42,8 100,8 Z", front: "M100,18 C148,18 168,42 178,80 C150,48 120,52 100,60 C80,52 50,48 22,80 C32,42 52,18 100,18 Z" },
            "Coily": { bg: "M100,5 C165,5 205,50 205,112 C205,132 199,148 190,160 L182,157 C178,112 160,48 100,48 C40,48 22,112 18,157 L10,160 C1,148 -5,132 -5,112 C-5,50 35,5 100,5 Z", front: "M100,15 C158,15 180,42 190,80 C160,42 122,48 100,58 C78,48 40,42 10,80 C20,42 42,15 100,15 Z" }
        },
        female: {
            "Straight": { bg: "M100,10 C155,10 200,45 200,105 C200,155 185,185 160,200 L155,200 C155,170 160,130 160,100 C160,55 135,35 100,35 C65,35 40,55 40,100 C40,130 45,170 45,200 L40,200 C15,185 0,155 0,105 C0,45 45,10 100,10 Z", front: "M100,20 C140,20 160,40 170,80 C145,55 120,55 100,60 C80,55 55,55 30,80 C40,40 60,20 100,20 Z" },
            "Wavy": { bg: "M100,10 C155,10 205,50 205,110 C205,160 185,190 155,205 C155,175 162,135 160,100 C160,55 135,35 100,35 C65,35 40,55 40,100 C38,135 45,175 45,205 C15,190 -5,160 -5,110 C-5,50 45,10 100,10 Z", front: "M100,20 C140,20 160,40 170,80 C145,55 120,55 100,60 C80,55 55,55 30,80 C40,40 60,20 100,20 Z" },
            "Curly": { bg: "M100,5 C165,5 210,50 210,115 C210,165 185,200 150,210 C145,175 155,130 155,100 C155,55 130,30 100,30 C70,30 45,55 45,100 C45,130 55,175 50,210 C15,200 -10,165 -10,115 C-10,50 35,5 100,5 Z", front: "M100,15 C148,15 168,42 178,80 C150,45 122,52 100,60 C78,52 50,45 22,80 C32,42 52,15 100,15 Z" },
            "Coily": { bg: "M100,-5 C175,-5 218,50 218,118 C218,168 188,210 148,215 C142,178 154,130 152,100 C152,52 128,25 100,25 C72,25 48,52 48,100 C46,130 58,178 52,215 C12,210 -18,168 -18,118 C-18,50 25,-5 100,-5 Z", front: "M100,10 C158,10 178,42 188,80 C158,40 122,46 100,56 C78,46 42,40 12,80 C22,42 42,10 100,10 Z" }
        },
        generic: {
            "Straight": { bg: "M100,10 C150,10 190,40 190,100 C190,120 180,140 170,160 L160,160 C160,100 140,50 100,50 C60,50 40,100 40,160 L30,160 C20,140 10,120 10,100 C10,40 50,10 100,10 Z", front: "M100,20 C140,20 160,40 170,80 C145,55 120,55 100,60 C80,55 55,55 30,80 C40,40 60,20 100,20 Z" },
            "Wavy": { bg: "M100,10 C150,10 195,50 195,110 C195,130 185,150 175,170 L160,160 C160,100 140,50 100,50 C60,50 40,100 40,160 L25,170 C15,150 5,130 5,110 C5,50 50,10 100,10 Z", front: "M100,20 C140,20 160,40 170,80 C145,55 120,55 100,60 C80,55 55,55 30,80 C40,40 60,20 100,20 Z" },
            "Curly": { bg: "M100,0 C160,0 200,40 200,100 C200,140 180,180 150,180 C140,150 140,100 100,50 C60,100 60,150 50,180 C20,180 0,140 0,100 C0,40 40,0 100,0 Z", front: "M100,15 C150,15 170,40 180,80 C150,45 120,50 100,60 C80,50 50,45 20,80 C30,40 50,15 100,15 Z" },
            "Coily": { bg: "M100,-10 C170,-10 210,40 210,100 C210,150 180,190 140,190 C130,150 140,100 100,50 C60,100 70,150 60,190 C20,190 -10,150 -10,100 C-10,40 30,-10 100,-10 Z", front: "M100,10 C160,10 180,40 190,80 C160,40 120,45 100,55 C80,45 40,40 10,80 C20,40 40,10 100,10 Z" }
        }
    };

    // Skin Color
    document.querySelectorAll('input[name="skin_color"]').forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                const paths = getAvatarPaths();
                if (paths.face) paths.face.style.fill = this.parentElement.style.backgroundColor;
            }
        });
    });

    // Hair Color
    document.querySelectorAll('input[name="hair_color"]').forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                const c = this.parentElement.style.backgroundColor;
                const paths = getAvatarPaths();
                if (paths.hairBg) paths.hairBg.style.fill = c;
                if (paths.hairFront) paths.hairFront.style.fill = c;
            }
        });
    });

    // Hair Type
    const hairTypeSelect = document.querySelector('select[name="hair_type"]');
    if (hairTypeSelect) {
        hairTypeSelect.addEventListener('change', function() {
            const key = userGender === 'male' ? 'male' : (userGender === 'female' ? 'female' : 'generic');
            const shapes = hairShapeMap[key];
            if (shapes && shapes[this.value]) {
                const paths = getAvatarPaths();
                if (paths.hairBg) paths.hairBg.setAttribute('d', shapes[this.value].bg);
                if (paths.hairFront) paths.hairFront.setAttribute('d', shapes[this.value].front);
            }
            const el = document.getElementById('preview-hair-type');
            if (el) el.innerText = this.value || 'Awaiting…';
        });
    }

    // Skin Type
    const skinTypeSelect = document.querySelector('select[name="skin_type"]');
    if (skinTypeSelect) skinTypeSelect.addEventListener('change', function() {
        const el = document.getElementById('preview-skin-type');
        if (el) el.innerText = this.value || 'Awaiting…';
    });

    // Scalp
    const scalpTypeSelect = document.querySelector('select[name="scalp_condition"]');
    if (scalpTypeSelect) scalpTypeSelect.addEventListener('change', function() {
        const el = document.getElementById('preview-scalp-type');
        if (el) el.innerText = this.value || 'Awaiting…';
    });

    // Oil Level
    const oilRange = document.querySelector('input[name="oil_level"]');
    if (oilRange) oilRange.addEventListener('input', function() {
        const labels = { '1': 'Low', '2': 'Medium', '3': 'High' };
        const el = document.getElementById('preview-oil-level');
        if (el) el.innerText = labels[this.value] || this.value;
    });

    // Lifestyle
    document.querySelectorAll('input[name="lifestyle"]').forEach(r => {
        r.addEventListener('change', function() {
            if (this.checked) {
                const el = document.getElementById('preview-lifestyle');
                if (el) el.innerText = this.value;
            }
        });
    });

    // Tags
    const tagContainer = document.getElementById('preview-tags-container');
    const dynamicCheckboxes = document.querySelectorAll('input[type="checkbox"]');
    function updateTags() {
        if (!tagContainer) return;
        tagContainer.innerHTML = '';
        dynamicCheckboxes.forEach(box => {
            if (box.checked) {
                const span = document.createElement('span');
                span.className = 'preview-tag';
                span.innerText = box.value;
                tagContainer.appendChild(span);
            }
        });
    }
    dynamicCheckboxes.forEach(box => box.addEventListener('change', updateTags));

    // Reflow for cached browser values
    document.querySelectorAll('input[type="radio"]:checked, input[type="checkbox"]:checked, select').forEach(el => {
        if (el.value && el.value !== "") el.dispatchEvent(new Event('change'));
    });
    document.querySelectorAll('input[type="range"]').forEach(el => el.dispatchEvent(new Event('input')));

    // --- Age Group Visual Changes ---
    const userAge = window.AppConfig?.age || 25;
    const ageGroup = userAge <= 30 ? '18-30' : (userAge <= 50 ? '30-50' : '50+');

    function showEl(id, val) {
        const el = document.getElementById(id);
        if (el) el.style.opacity = val;
    }
    function setFill(id, color) {
        const el = document.getElementById(id);
        if (el) el.style.fill = color;
    }

    if (ageGroup === '30-50') {
        // Subtle: crow's feet + faint nasolabial lines
        ['f-crow-feet','f-crow-feet-left','f-smile-lines','f-smile-lines-r'].forEach(id => showEl(id, '1'));
        ['m-crow-feet','m-crow-feet-left','m-smile-lines','m-smile-lines-r'].forEach(id => showEl(id, '1'));
    } else if (ageGroup === '50+') {
        // All wrinkles + forehead lines + grey hair/temples
        ['f-crow-feet','f-crow-feet-left','f-smile-lines','f-smile-lines-r','f-wrinkle-forehead','f-wrinkle-forehead2'].forEach(id => showEl(id, '1'));
        ['m-crow-feet','m-crow-feet-left','m-smile-lines','m-smile-lines-r','m-wrinkle-forehead','m-wrinkle-forehead2'].forEach(id => showEl(id, '1'));
        // Grey hair hint on female bangs
        setFill('f-grey-hair', 'rgba(200,200,200,0.38)');
        // Grey temples on male
        setFill('m-grey-temple-l', 'rgba(180,180,180,0.65)');
        setFill('m-grey-temple-r', 'rgba(180,180,180,0.65)');
    }
    // 18-30: no overlays shown (fresh & smooth)
});
