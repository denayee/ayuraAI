function startEditName() {
    document.getElementById('name-display').style.display = 'none';
    document.getElementById('name-edit-form').style.display = 'flex';
    const input = document.getElementById('name-input');
    input.focus();
    input.select();
}

function cancelEditName() {
    document.getElementById('name-display').style.display = '';
    document.getElementById('name-edit-form').style.display = 'none';
    document.getElementById('name-input').value = document.getElementById('name-text').textContent.trim();
}

async function saveName() {
    const input = document.getElementById('name-input');
    const newName = input.value.trim();
    if (!newName) { input.focus(); return; }

    const saveBtn = document.querySelector('.name-save-btn');
    saveBtn.textContent = '...';
    saveBtn.disabled = true;

    try {
        const { response, result } = await window.AyuraApi.jsonRequest(window.UPDATE_NAME_ENDPOINT, {
            method: 'POST',
            data: { name: newName },
        });

        if (response.ok && result.success) {
            document.getElementById('name-text').textContent = result.name;
            document.getElementById('header-name-text').textContent = result.name;
            document.querySelector('.account-avatar').textContent = result.name[0].toUpperCase();
            cancelEditName();
        } else {
            alert(result.error || 'Failed to update name');
        }
    } catch (err) {
        alert('Network error. Please try again.');
    } finally {
        saveBtn.textContent = '✓';
        saveBtn.disabled = false;
    }
}

document.getElementById('name-input').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') saveName();
    if (e.key === 'Escape') cancelEditName();
});
