from flask import Flask, session, redirect, url_for
from routes.auth_routes        import auth_bp
from routes.doctor_routes      import doctor_bp
from routes.patient_routes     import patient_bp
from routes.appointment_routes import appointment_bp

app = Flask(__name__)
app.secret_key = "hospital_secret_key_2024"

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
    # No init_db() needed — Firestore collections are created on first write
    app.run(debug=True)
