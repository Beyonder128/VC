from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from firebase_db import (
    book_appointment, cancel_appointment, confirm_waiting,
    get_all_doctors, get_patient_by_user, get_doctor_by_user,
    get_available_slots, get_specializations,
    get_appointments_for_patient, get_waiting_for_patient,
    get_appointments_for_doctor, get_waiting_for_doctor
)
from functools import wraps

appointment_bp = Blueprint("appointments", __name__)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def patient_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "patient":
            flash("Access denied — patients only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def doctor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "doctor":
            flash("Access denied — doctors only.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


# ── Patient: book an appointment ──────────────────────────────────────────────

@appointment_bp.route("/book", methods=["GET", "POST"])
@patient_required
def book():
    doctors         = get_all_doctors()
    specializations = get_specializations()
    patient         = get_patient_by_user(session["user_id"])

    if patient is None:
        flash("Patient profile not found. Please contact support.", "danger")
        return redirect(url_for("auth.logout"))

    if request.method == "POST":
        doctor_id = request.form.get("doctor_id", "").strip()
        appt_date = request.form.get("appt_date", "").strip()
        time_slot = request.form.get("time_slot", "").strip()

        if not all([doctor_id, appt_date, time_slot]):
            flash("All fields are required.", "danger")
        else:
            result = book_appointment(doctor_id, patient["id"], appt_date, time_slot)
            messages = {
                "booked":      ("Appointment confirmed! ✅", "success"),
                "slot_taken":  ("Slot already taken — you've been added to the waiting list. 🕐", "warning"),
                "future_date": ("Date is more than 2 days ahead — added to waiting list for doctor approval. 📋", "warning"),
            }
            flash(*messages[result])
            return redirect(url_for("patients.patient_dashboard"))

    return render_template(
        "book.html",
        doctors=doctors,
        specializations=specializations,
        patient=patient
    )


# ── Patient: cancel their own appointment ─────────────────────────────────────

# ID is now a Firestore string — use <string:appointment_id>
@appointment_bp.route("/cancel/<string:appointment_id>", methods=["POST"])
@patient_required
def cancel(appointment_id):
    patient = get_patient_by_user(session["user_id"])
    if patient is None:
        flash("Patient profile not found.", "danger")
        return redirect(url_for("auth.logout"))
    success = cancel_appointment(appointment_id, patient_id=patient["id"])
    if success:
        flash("Appointment cancelled. ✅", "success")
    else:
        flash("Appointment not found or not yours.", "danger")
    return redirect(url_for("patients.patient_dashboard"))


# ── Doctor: confirm a future_date waiting entry ───────────────────────────────

@appointment_bp.route("/confirm-waiting/<string:waiting_id>", methods=["POST"])
@doctor_required
def confirm_waiting_route(waiting_id):
    doctor = get_doctor_by_user(session["user_id"])
    if doctor is None:
        flash("Doctor profile not found.", "danger")
        return redirect(url_for("auth.logout"))
    result = confirm_waiting(waiting_id, doctor["id"])
    if result == "confirmed":
        flash("Appointment confirmed from waiting list! ✅", "success")
    elif result == "slot_now_taken":
        flash("Slot was taken in the meantime — entry moved to slot-taken queue. ⚠️", "warning")
    else:
        flash("Entry not found or not assigned to you.", "danger")
    return redirect(url_for("doctors.doctor_dashboard"))


# ── JSON: available slots for booking page ────────────────────────────────────

# doctor_id is a Firestore string ID
@appointment_bp.route("/api/slots/<string:doctor_id>")
@login_required
def available_slots(doctor_id):
    appt_date = request.args.get("date", "")
    if not appt_date:
        return jsonify([])
    return jsonify(get_available_slots(doctor_id, appt_date))
