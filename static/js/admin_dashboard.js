/**
 * Admin Dashboard JavaScript
 * Consolidates all administrative frontend logic.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Tab switching logic with persistence
    window.openTab = (evt, tabName) => {
        const tabcontent = document.getElementsByClassName("tab-content");
        for (let i = 0; i < tabcontent.length; i++) {
            tabcontent[i].style.display = "none";
        }
        const tablinks = document.getElementsByClassName("tab-btn");
        for (let i = 0; i < tablinks.length; i++) {
            tablinks[i].classList.remove("active");
        }
        document.getElementById(tabName).style.display = "block";
        if (evt) {
            evt.currentTarget.classList.add("active");
        } else {
            document.querySelector(`[onclick*="'${tabName}'"]`).classList.add("active");
        }
        localStorage.setItem('activeAdminTab', tabName);
    };

    // Restore active tab on load
    const lastTab = localStorage.getItem('activeAdminTab') || 'support';
    openTab(null, lastTab);

    // Status update handler
    window.updateStatus = async (id, status) => {
        try {
            const res = await fetch(`/admin/support/${id}/status`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({status: status})
            });
            if (res.ok) location.reload();
        } catch (err) {
            console.error("Status update failed:", err);
        }
    };

    // Generic entry deletion
    window.deleteEntry = async (type, id) => {
        if(!confirm(`Are you sure you want to delete this ${type}?`)) return;
        try {
            const res = await fetch(`/admin/${type}/${id}/delete`, {
                method: 'POST'
            });
            if (res.ok) location.reload();
        } catch (err) {
            console.error("Deletion failed:", err);
        }
    };

    // Webinar registration deletion
    window.deleteWebinarReg = async (id) => {
        if(!confirm('Are you sure you want to delete this registration?')) return;
        try {
            const res = await fetch(`/admin/webinar-reg/${id}/delete`, {
                method: 'POST'
            });
            if (res.ok) location.reload();
        } catch (err) {
            console.error("Registration deletion failed:", err);
        }
    };

    // Toggle registrations view for webinars
    window.toggleRegistrations = (webinarId) => {
        const el = document.getElementById(`regs-${webinarId}`);
        if (el.style.display === 'none' || !el.style.display) {
            el.style.display = 'block';
        } else {
            el.style.display = 'none';
        }
    };

    // AJAX Form Submission for "Schedule New Webinar"
    const webinarForm = document.querySelector('#webinar-manage form');
    if (webinarForm) {
        webinarForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(webinarForm);
            try {
                const res = await fetch(webinarForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                });
                const result = await res.json();
                if (res.ok) {
                    showToast(result.message || "Webinar scheduled successfully! 🛰️", "success");
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showToast(result.error || "Error scheduling webinar.", "error");
                }
            } catch (err) {
                showToast("System error. Please try again.", "error");
            }
        });
    }

    // Toast Notification logic
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            padding: 12px 25px;
            border-radius: 50px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            z-index: 9999;
            font-weight: 600;
            animation: slideDown 0.3s ease-out;
        `;
        toast.textContent = message;
        document.body.appendChild(toast);
        setTimeout(() => {
            toast.style.animation = 'slideUp 0.3s ease-in forwards';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});

// Animations for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideDown {
        from { transform: translate(-50%, -100%); opacity: 0; }
        to { transform: translate(-50%, 0); opacity: 1; }
    }
    @keyframes slideUp {
        from { transform: translate(-50%, 0); opacity: 1; }
        to { transform: translate(-50%, -100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
