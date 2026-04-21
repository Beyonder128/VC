from flask import Blueprint, render_template, session, redirect, url_for, flash
from models import get_patient_by_user, get_appointments_for_patient, get_waiting_for_patient
from functools import wraps

patient_bp = Blueprint("patients", __name__)


def patient_required(f):
    """Decorator: only logged-in patients can access this route."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "patient":
            flash("Access denied — patients only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@patient_bp.route("/patient/dashboard")
@patient_required
def patient_dashboard():
    patient      = get_patient_by_user(session["user_id"])
    appointments = get_appointments_for_patient(patient["id"])
    waiting      = get_waiting_for_patient(patient["id"])
    return render_template(
        "patient_dashboard.html",
        patient=patient,
        appointments=appointments,
        waiting=waiting
    )
