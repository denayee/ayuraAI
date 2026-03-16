from flask import Blueprint, request, jsonify, session
from database import get_db

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').lower()

    if not user_message:
        return jsonify({"response": "I didn't quite catch that. How can I help you today?"})

    # Login Help
    if any(keyword in user_message for keyword in ['login', 'log in', 'sign in']):
        if 'forgot' in user_message or 'password' in user_message:
            return jsonify({"response": "To reset your password:\n- Click 'Forgot Password' on the Login page\n- Enter your registered email\n- Follow the instructions sent to your email."})
        return jsonify({"response": "To login to your account:\n- Go to the Login page\n- Enter your registered email and password\n- Click the Login button."})

    # Registration Help
    if any(keyword in user_message for keyword in ['register', 'registration', 'signup', 'sign up', 'create account']):
        return jsonify({"response": "To register for an account:\n- Click the Sign Up or Register button\n- Enter your name and email address\n- Create a password\n- Click Register to create your account."})

    # Getting AI Recommendations
    if any(keyword in user_message for keyword in ['recommendation', 'analyze', 'analysis', 'skin', 'hair']):
        if 'allergy' in user_message or 'allergies' in user_message:
            return jsonify({"response": "Regarding Allergy Safety:\n- You can enter allergy information in the analysis form.\n- Our system filters out products containing ingredients you're allergic to.\n- Only safe products and remedies are recommended."})
        return jsonify({"response": "To get personalized recommendations:\n- Login to your account\n- Open the Skin and Hair Analysis form\n- Enter your skin and hair type, and select any problems (acne, dandruff, etc.)\n- Mention any allergies and submit the form\n- Our AI will then recommend suitable products and home remedies."})

    # Customer Service
    if any(keyword in user_message for keyword in ['customer service', 'support person', 'talk to someone']):
        if any(keyword in user_message for keyword in ['chat', 'phone', 'call']):
            if 'phone' in user_message or 'call' in user_message:
                return jsonify({"response": "Our phone support is available at +1-800-AYURA-AI from 9 AM to 6 PM EST. How else can I help?"})
            return jsonify({"response": "I'm connecting you to a live agent... Please wait a moment. (Note: This is a demo; in a real system, you'd be put in a queue.)"})
        return jsonify({"response": "How would you like to contact our customer service team? Please select an option:"})

    # Home Remedies
    if any(keyword in user_message for keyword in ['home remedy', 'home remedies', 'natural']):
         return jsonify({"response": "Our system provides comprehensive home remedies including:\n- Required ingredients\n- Preparation methods\n- Step-by-step application instructions\n- Recommended frequency. What else would you like to know?"})

    # Default response
    return jsonify({"response": "I'm here to help with login, registration, and how to use the cosmetic recommendation system. Please ask a related question."})

@chatbot_bp.route('/support-request', methods=['POST'])
def support_request():
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    phone = data.get('phone', '').strip()
    message = data.get('message', '').strip()
    user_id = session.get('user_id')

    db = get_db()
    # Auto-fetch name and email if user is logged in
    if user_id:
        try:
            user = db.execute('SELECT name, email FROM users WHERE id = ?', (user_id,)).fetchone()
            if user:
                if not name:
                    name = user['name']
                if not email:
                    email = user['email']
        except Exception as e:
            print(f"Error fetching user details: {e}")

    # Basic validations (now using potentially auto-fetched details)
    import re
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    phone_regex = r'^[0-9]{10}$'

    if not all([name, email, phone]):
        return jsonify({"success": False, "message": "All fields are required."}), 400
    
    if len(name) < 2 or len(name) > 50:
        return jsonify({"success": False, "message": "Invalid name length."}), 400
        
    if not re.match(email_regex, email):
        return jsonify({"success": False, "message": "Invalid email format."}), 400
        
    if not re.match(phone_regex, phone):
        return jsonify({"success": False, "message": "Invalid phone format. Must be 10 digits."}), 400

    try:
        cur = db.cursor()
        cur.execute("""
            INSERT INTO support_requests (user_id, name, email, phone, message)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, name, email, phone, message))
        db.commit()
        return jsonify({"success": True, "message": "Your request has been saved. A customer executive will reach you soon."})
    except Exception as e:
        print(f"Error saving support request: {e}")
        return jsonify({"success": False, "message": "An error occurred while saving your request."}), 500
    finally:
        db.close()
