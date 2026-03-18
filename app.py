from flask import Flask, render_template, session, redirect, url_for
from auth.register import register_bp
from auth.login import login_bp
from auth.google_auth import google_auth_bp, init_google_oauth
from routes.character_builder import character_bp
from routes.recommendation import recommendation_bp
from routes.ai_implement import ai_implement
from routes.ML_prediction import prediction_bp
from routes.account import account_bp
from routes.product_search import product_search_bp
from routes.chatbot import chatbot_bp
from routes.footer_pages import pages_bp
from routes.admin import admin_bp
from flask_mail import Mail
from dotenv import load_dotenv
from flask_cors import CORS
import os
import create_db

app = Flask(__name__)
CORS(app)
load_dotenv()
if not os.path.exists("database.db"):
    create_db.create_database()

# Generate a random SECRET_KEY every time the server starts
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "your-secret-key")

# Mail Configuration
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

mail = Mail(app)

# Initialize Google OAuth
init_google_oauth(app)


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("recommendation.recommendation"))
    return render_template("index.html")


# Test Route (for Render deployment check)
@app.route("/test")
def test():
    return "Backend Working ✅"


# Register Blueprints
app.register_blueprint(register_bp, url_prefix="/auth")
app.register_blueprint(login_bp, url_prefix="/auth")
app.register_blueprint(google_auth_bp, url_prefix="/auth")
app.register_blueprint(character_bp, url_prefix="/routes")
app.register_blueprint(recommendation_bp, url_prefix="/routes")
app.register_blueprint(ai_implement, url_prefix="/routes")
app.register_blueprint(prediction_bp)
app.register_blueprint(account_bp, url_prefix="/routes")
app.register_blueprint(product_search_bp, url_prefix="/api")
app.register_blueprint(chatbot_bp, url_prefix="/api")
app.register_blueprint(pages_bp, url_prefix="/routes")
app.register_blueprint(admin_bp)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
