from flask import Flask, render_template, session, redirect, url_for
from auth.register import register_bp
from auth.login import login_bp
from routes.character_builder import character_bp
from routes.recommendation import recommendation_bp
from routes.ai_implement import ai_implement
from dotenv import load_dotenv
import os

app = Flask(__name__)
load_dotenv()
app.config["SECRET_KEY"] = os.urandom(
    24
)  # Random key on every restart to invalidate sessions


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


# Register Blueprints
app.register_blueprint(register_bp, url_prefix="/auth")
app.register_blueprint(login_bp, url_prefix="/auth")
app.register_blueprint(character_bp, url_prefix="/routes")
app.register_blueprint(recommendation_bp, url_prefix="/routes")
app.register_blueprint(ai_implement, url_prefix="/routes")

if __name__ == "__main__":
    app.run(debug=True)
