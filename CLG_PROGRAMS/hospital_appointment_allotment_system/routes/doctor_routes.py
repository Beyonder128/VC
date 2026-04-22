from flask import Blueprint, render_template, redirect, url_for, flash, session
from firebase_db import get_doctor_by_user, get_appointments_for_doctor, get_waiting_for_doctor
from functools import wraps

doctor_bp = Blueprint("doctors", __name__)


def doctor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "doctor":
            flash("Access denied — doctors only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@doctor_bp.route("/doctor/dashboard")
@doctor_required
def doctor_dashboard():
    doctor = get_doctor_by_user(session["user_id"])
    if doctor is None:
        flash("Doctor profile not found. Please re-register.", "danger")
        return redirect(url_for("auth.logout"))
    appointments = get_appointments_for_doctor(doctor["id"])
    waiting      = get_waiting_for_doctor(doctor["id"])
    return render_template(
        "doctor_dashboard.html",
        doctor=doctor,
        appointments=appointments,
        waiting=waiting
    )
