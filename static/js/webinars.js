/**
 * Public Webinars Page JavaScript
 */
document.addEventListener('DOMContentLoaded', () => {
    const notificationContainer = document.getElementById('notification-container');

    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('toggle-btn')) {
            const id = e.target.dataset.webinarId;
            document.getElementById(`registration-form-container-${id}`).style.display = 'block';
            e.target.style.display = 'none';
        }

        if (e.target.classList.contains('close-btn')) {
            const id = e.target.dataset.webinarId;
            document.getElementById(`registration-form-container-${id}`).style.display = 'none';
            document.getElementById(`toggle-registration-${id}`).style.display = 'inline-block';
        }
    });

    function showNotification(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `contact-${type} floating-toast`;
        toast.innerHTML = `
            <div style="flex-grow: 1;">${message}</div>
            <span style="cursor: pointer; font-size: 1.5rem; margin-left: 20px; line-height: 1; font-weight: bold;" onclick="this.parentElement.remove()">x</span>
        `;
        toast.style.cssText = `
            pointer-events: auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            text-align: center;
            padding: 18px 25px;
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            animation: slideDown 0.3s ease-out;
            width: 100%;
        `;
        notificationContainer.appendChild(toast);

        setTimeout(() => {
            if (toast.parentElement) {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(-20px)';
                setTimeout(() => toast.remove(), 500);
            }
        }, 5000);
    }

    document.addEventListener('submit', async (e) => {
        if (!e.target.classList.contains('dynamic-webinar-form')) return;

        e.preventDefault();
        const form = e.target;
        const webinarId = form.querySelector('input[name="webinar_id"]').value;

        document.querySelectorAll('.error-feedback').forEach(el => {
            el.textContent = '';
        });

        try {
            const { response, result } = await window.AyuraApi.jsonRequest(form.dataset.endpoint, {
                method: 'POST',
                data: window.AyuraApi.formToJson(form),
            });

            if (response.ok && result.success) {
                showNotification(result.message, 'success');
                form.reset();
                setTimeout(() => {
                    const container = document.getElementById(`registration-form-container-${webinarId}`);
                    if (container) container.style.display = 'none';
                    const toggle = document.getElementById(`toggle-registration-${webinarId}`);
                    if (toggle) toggle.style.display = 'inline-block';
                }, 3000);
            } else if (result.errors) {
                Object.entries(result.errors).forEach(([field, message]) => {
                    const errorEl = document.getElementById(`error-${field}-${webinarId}`);
                    if (errorEl) errorEl.textContent = message;
                });
                showNotification('Please correct the entries.', 'error');
            } else {
                showNotification(result.error || 'Registration failed.', 'error');
            }
        } catch (err) {
            showNotification('Registration failed. Please try again later.', 'error');
        }
    });

    if (!document.getElementById('webinar-js-styles')) {
        const style = document.createElement('style');
        style.id = 'webinar-js-styles';
        style.textContent = `
            @keyframes slideDown {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .floating-toast {
                transition: all 0.5s ease;
            }
        `;
        document.head.appendChild(style);
    }
});
