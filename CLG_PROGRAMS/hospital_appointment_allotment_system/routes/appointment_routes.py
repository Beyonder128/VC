from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from firebase_db import (
    book_appointment, cancel_appointment, confirm_waiting,
    get_all_doctors, get_patient_by_user, get_doctor_by_user,
    get_available_slots, get_specializations,
    get_appointments_for_patient, get_waiting_for_patient,
    get_appointments_for_doctor, get_waiting_for_doctor,
    get_doctor_email, get_patient_email,
    _get_doctor_data, _get_patient_data,
)
from utils.email_service import (
    send_booking_confirmation_to_patient,
    send_booking_email_to_doctor,
    send_waiting_list_email,
    send_approval_request_to_doctor,
    send_future_date_pending_to_patient,
    send_final_confirmation_email,
)
from functools import wraps

appointment_bp = Blueprint("appointments", __name__)


# ── Auth decorators ───────────────────────────────────────────────────────────

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


# ── Internal: resolve names + emails for notifications ───────────────────────

def _get_booking_context(doctor_id: str, patient_id: str) -> dict:
    """
    Fetch all data needed to send emails for a booking event.
    Centralised here so each route doesn't repeat the same lookups.
    Returns a flat dict with doctor/patient names, emails, specialization.
    """
    doctor  = _get_doctor_data(doctor_id)
    patient = _get_patient_data(patient_id)
    return {
        "doctor_name":    doctor.get("name", "Unknown"),
        "specialization": doctor.get("specialization", ""),
        "patient_name":   patient.get("name", "Unknown"),
        "doctor_email":   get_doctor_email(doctor_id),
        "patient_email":  get_patient_email(patient_id),
    }


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

            # Resolve names + emails once for all email functions below
            ctx = _get_booking_context(doctor_id, patient["id"])

            if result == "booked":
                flash("Appointment confirmed! ✅", "success")

                # ── Email: patient gets confirmation ──────────────────────────
                send_booking_confirmation_to_patient(
                    patient_email  = ctx["patient_email"],
                    patient_name   = ctx["patient_name"],
                    doctor_name    = ctx["doctor_name"],
                    specialization = ctx["specialization"],
                    appt_date      = appt_date,
                    time_slot      = time_slot,
                )
                # ── Email: doctor notified of new booking ─────────────────────
                send_booking_email_to_doctor(
                    doctor_email  = ctx["doctor_email"],
                    doctor_name   = ctx["doctor_name"],
                    patient_name  = ctx["patient_name"],
                    appt_date     = appt_date,
                    time_slot     = time_slot,
                )

            elif result == "slot_taken":
                flash("Slot already taken — you've been added to the waiting list. 🕐", "warning")

                # ── Email: patient told they're on waiting list ────────────────
                send_waiting_list_email(
                    patient_email  = ctx["patient_email"],
                    patient_name   = ctx["patient_name"],
                    doctor_name    = ctx["doctor_name"],
                    specialization = ctx["specialization"],
                    appt_date      = appt_date,
                    time_slot      = time_slot,
                )

            elif result == "future_date":
                flash("Date is more than 2 days ahead — added to waiting list for doctor approval. 📋", "warning")

                # ── Email: patient told approval is pending ───────────────────
                send_future_date_pending_to_patient(
                    patient_email  = ctx["patient_email"],
                    patient_name   = ctx["patient_name"],
                    doctor_name    = ctx["doctor_name"],
                    specialization = ctx["specialization"],
                    appt_date      = appt_date,
                    time_slot      = time_slot,
                )
                # ── Email: doctor asked to approve ────────────────────────────
                send_approval_request_to_doctor(
                    doctor_email  = ctx["doctor_email"],
                    doctor_name   = ctx["doctor_name"],
                    patient_name  = ctx["patient_name"],
                    appt_date     = appt_date,
                    time_slot     = time_slot,
                )

            return redirect(url_for("patients.patient_dashboard"))

    return render_template(
        "book.html",
        doctors=doctors,
        specializations=specializations,
        patient=patient,
    )


# ── Patient: cancel their own appointment ─────────────────────────────────────

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

    # Fetch waiting entry BEFORE confirming so we have patient_id for email
    from firebase_db import db, WAITING
    w_doc = db.collection(WAITING).document(waiting_id).get()

    result = confirm_waiting(waiting_id, doctor["id"])

    if result == "confirmed":
        flash("Appointment confirmed from waiting list! ✅", "success")

        # Send final confirmation email to patient
        if w_doc.exists:
            entry      = w_doc.to_dict()
            ctx        = _get_booking_context(entry["doctor_id"], entry["patient_id"])
            send_final_confirmation_email(
                patient_email  = ctx["patient_email"],
                patient_name   = ctx["patient_name"],
                doctor_name    = ctx["doctor_name"],
                specialization = ctx["specialization"],
                appt_date      = entry["appt_date"],
                time_slot      = entry["time_slot"],
            )

    elif result == "slot_now_taken":
        flash("Slot was taken in the meantime — entry moved to slot-taken queue. ⚠️", "warning")
    else:
        flash("Entry not found or not assigned to you.", "danger")

    return redirect(url_for("doctors.doctor_dashboard"))


# ── JSON: available slots for booking page ────────────────────────────────────

@appointment_bp.route("/api/slots/<string:doctor_id>")
@login_required
def available_slots(doctor_id):
    appt_date = request.args.get("date", "")
    if not appt_date:
        return jsonify([])
    return jsonify(get_available_slots(doctor_id, appt_date))
