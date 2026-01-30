from flask import Flask, render_template
from auth.register import register_bp
from auth.login import login_bp
from routes.character_builder import character_bp
from routes.recommendation import recommendation_bp

app = Flask(__name__)
app.secret_key = "secretkey123"


@app.route("/")
def home():
    return render_template("index.html")


# Register Blueprints
app.register_blueprint(register_bp)
app.register_blueprint(login_bp)
app.register_blueprint(character_bp)
app.register_blueprint(recommendation_bp)

if __name__ == "__main__":
    app.run(debug=True)
