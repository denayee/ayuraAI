from flask import current_app, render_template, url_for
from flask_mail import Message
from premailer import transform
import os

def _get_inlined_html(template_name, **context):
    """Helper to render and inline CSS for an email template."""
    try:
        html_body = render_template(template_name, **context)
        css_path = os.path.join(current_app.static_folder, "css", "email.css")
        if os.path.exists(css_path):
            with open(css_path, "r") as f:
                css_content = f.read()
            html_with_css = html_body.replace("</head>", f"<style>{css_content}</style></head>")
            return transform(html_with_css)
        return html_body
    except Exception as e:
        print(f"Error inlining CSS for {template_name}: {e}")
        return render_template(template_name, **context)

def send_welcome_email(email, name):
    """Sends a premium welcome email to a new user."""
    try:
        start_url = url_for("recommendation.recommendation", _external=True)
        mail = current_app.extensions.get("mail")
        if not mail:
            return False
            
        html_body = _get_inlined_html("email/welcome_email.html", name=name, start_url=start_url)
        
        msg = Message(
            "Welcome to AyuraAI! ✨",
            recipients=[email],
            body=f"Hello {name},\n\nWelcome to AyuraAI! Start your AI analysis here:\n\n{start_url}",
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending welcome email to {email}: {e}")
        return False

def send_password_reset_email(email, reset_url):
    """Sends a professional password reset email."""
    try:
        mail = current_app.extensions.get("mail")
        if not mail:
            return False
            
        html_body = _get_inlined_html("email/reset_password_email.html", reset_url=reset_url)
        
        msg = Message(
            "Reset Your AyuraAI Password 🔒",
            recipients=[email],
            body=f"Please reset your password by clicking this link: {reset_url}",
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending reset email to {email}: {e}")
        return False

def send_contact_confirmation_email(email, name, message_snippet):
    """Sends a confirmation email after a user submits the contact form."""
    try:
        mail = current_app.extensions.get("mail")
        if not mail:
            return False
            
        html_body = _get_inlined_html("email/contact_confirmation_email.html", name=name, message_snippet=message_snippet)
        
        msg = Message(
            "We've Received Your Message - AyuraAI Support",
            recipients=[email],
            body=f"Hello {name},\n\nWe have received your message: \"{message_snippet}\"",
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending contact confirmation to {email}: {e}")
        return False

def send_webinar_registration_email(email, name, topic):
    """Sends a confirmation email after a user registers for a webinar."""
    try:
        mail = current_app.extensions.get("mail")
        if not mail:
            return False
            
        html_body = _get_inlined_html("email/webinar_registration_email.html", name=name, topic=topic)
        
        msg = Message(
            f"Registration Confirmed: {topic} 🎉",
            recipients=[email],
            body=f"Hello {name},\n\nYou're registered for: {topic}.",
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending webinar email to {email}: {e}")
        return False

def send_close_inquiry_email(email, name, message_snippet):
    """Sends a notification email when a support inquiry is resolved."""
    try:
        mail = current_app.extensions.get("mail")
        if not mail:
            return False
            
        html_body = _get_inlined_html("email/close_inquiry_email.html", name=name, message_snippet=message_snippet)
        
        msg = Message(
            "Your AyuraAI Support Inquiry Has Been Resolved ✅",
            recipients=[email],
            body=f"Hello {name},\n\nYour inquiry has been resolved: \"{message_snippet}\"",
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending close inquiry email to {email}: {e}")
        return False

def send_reopen_inquiry_email(email, name, message_snippet):
    """Sends a notification email when a support inquiry is re-opened."""
    try:
        mail = current_app.extensions.get("mail")
        if not mail:
            return False
            
        html_body = _get_inlined_html("email/reopen_inquiry_email.html", name=name, message_snippet=message_snippet)
        
        msg = Message(
            "Your AyuraAI Support Inquiry Has Been Re-opened 🔄",
            recipients=[email],
            body=f"Hello {name},\n\nYour inquiry has been re-opened: \"{message_snippet}\"",
            html=html_body
        )
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending re-open inquiry email to {email}: {e}")
        return False
