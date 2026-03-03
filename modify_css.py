import re

css_path = 'd:/ayuraAI/static/css/style.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

variables = """
:root {
    /* Light Mode */
    --bg-color: #F8F9FA;
    --surface-color: #FFFFFF;
    --text-primary: #15161C;
    --text-secondary: #64677A;
    --primary-color: #4DA1FF;
    --primary-hover: #3b82f6;
    --success-color: #4CE16A;
    --alert-color: #FF5A65;
    --idle-color: #FF9E2A;
    --border-color: #E2E4E8;
    --navbar-bg: #FFFFFF;
    --navbar-text: #15161C;
    --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

[data-theme="dark"] {
    /* Dark Mode */
    --bg-color: #15161C;
    --surface-color: #1C1E26;
    --text-primary: #FFFFFF;
    --text-secondary: #9699A6;
    --primary-color: #4DA1FF;
    --primary-hover: #3b82f6;
    --success-color: #4CE16A;
    --alert-color: #FF5A65;
    --idle-color: #FF9E2A;
    --border-color: #383A49;
    --navbar-bg: #1C1E26;
    --navbar-text: #FFFFFF;
    --card-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
}

body {
    background-color: var(--bg-color);
    color: var(--text-primary);
    transition: background-color 0.3s, color 0.3s;
}

"""

css = re.sub(r'body\s*\{[^}]*\}', '', css)

css = variables + css

css = css.replace('#f9f9f9', 'var(--bg-color)')
css = css.replace('#333', 'var(--text-primary)')
css = css.replace('#fff', 'var(--surface-color)')
# Need to be careful with 'white' and '#ffffff'
css = css.replace('white', 'var(--surface-color)')
css = css.replace('#2f8f83', 'var(--primary-color)')
css = css.replace('#4ccfc0', 'var(--primary-hover)')
css = css.replace('#f0f8f7', 'var(--bg-color)')
css = css.replace('#ddd', 'var(--border-color)')
css = css.replace('#444', 'var(--text-primary)')
css = css.replace('#666', 'var(--text-secondary)')
css = css.replace('#267f73', 'var(--primary-hover)')
css = css.replace('rgba(0,0,0,0.1)', 'var(--card-shadow)')
css = css.replace('rgba(0, 0, 0, 0.1)', 'var(--card-shadow)')
css = css.replace('background-color: #eef7f6', 'background-color: var(--surface-color)')
css = css.replace('background-color: #ffe6e6', 'background-color: var(--alert-color)')
css = css.replace('color: #cc0000', 'color: var(--surface-color)')
css = css.replace('color: var(--surface-color)', 'color: var(--bg-color)') # Fixing the button text colors if they are inside buttons, actually let's undo

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)

print('Updated style.css')
