/**
 * Admin Dashboard JavaScript
 * Consolidates all administrative frontend logic.
 */

document.addEventListener('DOMContentLoaded', () => {
    window.openTab = (evt, tabName) => {
        const tabcontent = document.getElementsByClassName('tab-content');
        for (let i = 0; i < tabcontent.length; i += 1) {
            tabcontent[i].style.display = 'none';
        }

        const tablinks = document.getElementsByClassName('tab-btn');
        for (let i = 0; i < tablinks.length; i += 1) {
            tablinks[i].classList.remove('active');
        }

        document.getElementById(tabName).style.display = 'block';
        if (evt) {
            evt.currentTarget.classList.add('active');
        } else {
            document.querySelector(`[onclick*="'${tabName}'"]`).classList.add('active');
        }
        localStorage.setItem('activeAdminTab', tabName);
    };

    const lastTab = localStorage.getItem('activeAdminTab') || 'support';
    openTab(null, lastTab);

    window.updateStatus = async (id, status) => {
        try {
            const { response } = await window.AyuraApi.jsonRequest(`/admin/support/${id}/status`, {
                method: 'POST',
                data: { status },
            });
            if (response.ok) location.reload();
        } catch (err) {
            console.error('Status update failed:', err);
        }
    };

    window.deleteEntry = async (type, id) => {
        if (!confirm(`Are you sure you want to delete this ${type}?`)) return;
        try {
            const { response } = await window.AyuraApi.jsonRequest(`/admin/${type}/${id}/delete`, {
                method: 'POST',
            });
            if (response.ok) location.reload();
        } catch (err) {
            console.error('Deletion failed:', err);
        }
    };

    window.deleteWebinarReg = async (id) => {
        if (!confirm('Are you sure you want to delete this registration?')) return;
        try {
            const { response } = await window.AyuraApi.jsonRequest(`/admin/webinar-reg/${id}/delete`, {
                method: 'POST',
            });
            if (response.ok) location.reload();
        } catch (err) {
            console.error('Registration deletion failed:', err);
        }
    };

    window.toggleRegistrations = (webinarId) => {
        const el = document.getElementById(`regs-${webinarId}`);
        if (el.style.display === 'none' || !el.style.display) {
            el.style.display = 'block';
        } else {
            el.style.display = 'none';
        }
    };

    const webinarForm = document.querySelector('#webinar-manage form');
    if (webinarForm) {
        webinarForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitButton = webinarForm.querySelector('button[type="submit"]');
            const originalText = submitButton.textContent;
            submitButton.disabled = true;
            submitButton.textContent = 'Scheduling...';

            try {
                const { response, result } = await window.AyuraApi.jsonRequest(webinarForm.dataset.endpoint, {
                    method: 'POST',
                    data: window.AyuraApi.formToJson(webinarForm),
                });

                if (response.ok && result.success) {
                    showToast(result.message || 'Webinar scheduled successfully!', 'success');
                    setTimeout(() => location.reload(), 1500);
                } else {
                    showToast(result.error || 'Error scheduling webinar.', 'error');
                }
            } catch (err) {
                showToast('System error. Please try again.', 'error');
            } finally {
                submitButton.disabled = false;
                submitButton.textContent = originalText;
            }
        });
    }

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
