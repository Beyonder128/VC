from flask import Flask, session, redirect, url_for
from flask_mail import Mail
from dotenv import load_dotenv
import os

from routes.auth_routes        import auth_bp
from routes.doctor_routes      import doctor_bp
from routes.patient_routes     import patient_bp
from routes.appointment_routes import appointment_bp

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "hospital_secret_key_2024")

# ── Flask-Mail configuration ──────────────────────────────────────────────────
app.config["MAIL_SERVER"]         = os.getenv("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"]            = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"]         = os.getenv("MAIL_USE_TLS", "True") == "True"
app.config["MAIL_USE_SSL"]         = False
app.config["MAIL_USERNAME"]        = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"]        = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"]  = os.getenv("MAIL_DEFAULT_SENDER")

# Initialize Flask-Mail
mail = Mail(app)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(appointment_bp)


@app.route("/")
def dashboard():
    """Root: redirect to role dashboard if logged in, else to login."""
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    if session["role"] == "doctor":
        return redirect(url_for("doctors.doctor_dashboard"))
    return redirect(url_for("patients.patient_dashboard"))


@app.route("/doctor/home")
def doctor_dash():
    return redirect(url_for("doctors.doctor_dashboard"))


@app.route("/patient/home")
def patient_dash():
    return redirect(url_for("patients.patient_dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
