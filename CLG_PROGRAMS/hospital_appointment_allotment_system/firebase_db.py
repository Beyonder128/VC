"""
firebase_db.py  —  All Firestore operations for MediBook.

Collections:
  users        — auth credentials + role
  doctors      — doctor profiles  (user_id FK)
  patients     — patient profiles (user_id FK)
  appointments — confirmed bookings
  waiting_list — queued entries (slot_taken | future_date)
"""

import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash

# ── Init ──────────────────────────────────────────────────────────────────────
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# ── Collection names ──────────────────────────────────────────────────────────
USERS        = "users"
DOCTORS      = "doctors"
PATIENTS     = "patients"
APPOINTMENTS = "appointments"
WAITING      = "waiting_list"


# ── Auth ──────────────────────────────────────────────────────────────────────

def register_user(username, password, role, extra):
    """
    Create user doc + role profile in one go.
    Returns user_id (str) on success, None if username taken.
    """
    existing = (
        db.collection(USERS)
        .where(filter=FieldFilter("username", "==", username))
        .limit(1).get()
    )
    if existing:
        return None

    user_ref = db.collection(USERS).document()
    user_ref.set({
        "username":      username,
        "password_hash": generate_password_hash(password),
        "role":          role,
    })
    user_id = user_ref.id

    if role == "doctor":
        db.collection(DOCTORS).document().set({
            "user_id":        user_id,
            "name":           extra["name"],
            "specialization": extra["specialization"],
        })
    else:
        db.collection(PATIENTS).document().set({
            "user_id": user_id,
            "name":    extra["name"],
            "age":     int(extra["age"]),
        })

    return user_id


def login_user(username, password):
    """Return user dict with 'id' key on success, None on failure."""
    docs = (
        db.collection(USERS)
        .where(filter=FieldFilter("username", "==", username))
        .limit(1).get()
    )
    if not docs:
        return None
    doc  = docs[0]
    data = doc.to_dict()
    if check_password_hash(data["password_hash"], password):
        return {**data, "id": doc.id}
    return None


# ── Doctor helpers ────────────────────────────────────────────────────────────

def get_doctor_by_user(user_id):
    docs = (
        db.collection(DOCTORS)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .limit(1).get()
    )
    if not docs:
        return None
    doc = docs[0]
    return {**doc.to_dict(), "id": doc.id}


def get_all_doctors(specialization=None):
    query = db.collection(DOCTORS)
    if specialization:
        query = query.where(filter=FieldFilter("specialization", "==", specialization))
    return [{**d.to_dict(), "id": d.id} for d in query.stream()]


def get_specializations():
    docs = db.collection(DOCTORS).stream()
    return sorted({d.to_dict()["specialization"] for d in docs})


# ── Patient helpers ───────────────────────────────────────────────────────────

def get_patient_by_user(user_id):
    docs = (
        db.collection(PATIENTS)
        .where(filter=FieldFilter("user_id", "==", user_id))
        .limit(1).get()
    )
    if not docs:
        return None
    doc = docs[0]
    return {**doc.to_dict(), "id": doc.id}


# ── Slot helpers ──────────────────────────────────────────────────────────────

ALL_SLOTS = [
    "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
    "11:00 AM", "11:30 AM", "12:00 PM", "02:00 PM",
    "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM",
]


def is_slot_taken(doctor_id, appt_date, time_slot):
    docs = (
        db.collection(APPOINTMENTS)
        .where(filter=FieldFilter("doctor_id", "==", doctor_id))
        .where(filter=FieldFilter("appt_date",  "==", appt_date))
        .where(filter=FieldFilter("time_slot",  "==", time_slot))
        .limit(1).get()
    )
    return len(docs) > 0


def is_future_date(appt_date_str):
    appt_dt = datetime.strptime(appt_date_str, "%Y-%m-%d").date()
    return (appt_dt - date.today()).days > 2


def get_available_slots(doctor_id, appt_date):
    booked_docs = (
        db.collection(APPOINTMENTS)
        .where(filter=FieldFilter("doctor_id", "==", doctor_id))
        .where(filter=FieldFilter("appt_date",  "==", appt_date))
        .stream()
    )
    booked = {d.to_dict()["time_slot"] for d in booked_docs}
    return [s for s in ALL_SLOTS if s not in booked]


# ── Appointment helpers ───────────────────────────────────────────────────────

def book_appointment(doctor_id, patient_id, appt_date, time_slot):
    """
    Rules (checked in order):
      1. Date > today+2  → waiting_list, reason='future_date'
      2. Slot taken      → waiting_list, reason='slot_taken'
      3. Free            → confirmed appointment
    Returns: 'future_date' | 'slot_taken' | 'booked'
    """
    if is_future_date(appt_date):
        _add_to_waiting(doctor_id, patient_id, appt_date, time_slot, "future_date")
        return "future_date"

    if is_slot_taken(doctor_id, appt_date, time_slot):
        _add_to_waiting(doctor_id, patient_id, appt_date, time_slot, "slot_taken")
        return "slot_taken"

    _insert_appointment(doctor_id, patient_id, appt_date, time_slot)
    return "booked"


def _add_to_waiting(doctor_id, patient_id, appt_date, time_slot, reason):
    db.collection(WAITING).document().set({
        "doctor_id":  doctor_id,
        "patient_id": patient_id,
        "appt_date":  appt_date,
        "time_slot":  time_slot,
        "reason":     reason,
        "created_at": firestore.SERVER_TIMESTAMP,
    })


def _insert_appointment(doctor_id, patient_id, appt_date, time_slot):
    db.collection(APPOINTMENTS).document().set({
        "doctor_id":  doctor_id,
        "patient_id": patient_id,
        "appt_date":  appt_date,
        "time_slot":  time_slot,
        "created_at": firestore.SERVER_TIMESTAMP,
    })


def _get_doctor_data(doctor_id):
    doc = db.collection(DOCTORS).document(doctor_id).get()
    return doc.to_dict() or {} if doc.exists else {}


def _get_patient_data(patient_id):
    doc = db.collection(PATIENTS).document(patient_id).get()
    return doc.to_dict() or {} if doc.exists else {}


def get_appointments_for_doctor(doctor_id):
    docs = (
        db.collection(APPOINTMENTS)
        .where(filter=FieldFilter("doctor_id", "==", doctor_id))
        .stream()
    )
    results = []
    for d in docs:
        data    = d.to_dict()
        patient = _get_patient_data(data["patient_id"])
        results.append({
            "id":           d.id,
            "patient_name": patient.get("name", "Unknown"),
            "appt_date":    data["appt_date"],
            "time_slot":    data["time_slot"],
        })
    return sorted(results, key=lambda x: (x["appt_date"], x["time_slot"]))


def get_appointments_for_patient(patient_id):
    docs = (
        db.collection(APPOINTMENTS)
        .where(filter=FieldFilter("patient_id", "==", patient_id))
        .stream()
    )
    results = []
    for d in docs:
        data   = d.to_dict()
        doctor = _get_doctor_data(data["doctor_id"])
        results.append({
            "id":             d.id,
            "doctor_name":    doctor.get("name", "Unknown"),
            "specialization": doctor.get("specialization", ""),
            "appt_date":      data["appt_date"],
            "time_slot":      data["time_slot"],
        })
    return sorted(results, key=lambda x: (x["appt_date"], x["time_slot"]))


def cancel_appointment(appointment_id, patient_id=None):
    """
    Cancel a confirmed appointment.
    Verifies patient ownership if patient_id is given.
    Auto-promotes first slot_taken waiting entry (sorted in Python — no index needed).
    """
    appt_ref = db.collection(APPOINTMENTS).document(appointment_id)
    appt_doc = appt_ref.get()

    if not appt_doc.exists:
        return False

    appt = appt_doc.to_dict()

    if patient_id and appt.get("patient_id") != patient_id:
        return False

    appt_ref.delete()

    # Fetch all slot_taken entries for this doctor+date+slot, sort in Python
    waiting_docs = (
        db.collection(WAITING)
        .where(filter=FieldFilter("doctor_id", "==", appt["doctor_id"]))
        .where(filter=FieldFilter("appt_date",  "==", appt["appt_date"]))
        .where(filter=FieldFilter("time_slot",  "==", appt["time_slot"]))
        .where(filter=FieldFilter("reason",     "==", "slot_taken"))
        .get()
    )

    if waiting_docs:
        # Sort by document ID (chronological proxy) — no composite index needed
        first = sorted(waiting_docs, key=lambda d: d.id)[0]
        wdata = first.to_dict()
        _insert_appointment(
            wdata["doctor_id"], wdata["patient_id"],
            wdata["appt_date"], wdata["time_slot"]
        )
        db.collection(WAITING).document(first.id).delete()

    return True


def confirm_waiting(waiting_id, doctor_id):
    """
    Doctor confirms a future_date waiting entry.
    Returns: 'confirmed' | 'slot_now_taken' | None
    """
    w_ref = db.collection(WAITING).document(waiting_id)
    w_doc = w_ref.get()

    if not w_doc.exists:
        return None

    entry = w_doc.to_dict()

    if entry.get("doctor_id") != doctor_id:
        return None

    if is_slot_taken(entry["doctor_id"], entry["appt_date"], entry["time_slot"]):
        w_ref.update({"reason": "slot_taken"})
        return "slot_now_taken"

    _insert_appointment(
        entry["doctor_id"], entry["patient_id"],
        entry["appt_date"], entry["time_slot"]
    )
    w_ref.delete()
    return "confirmed"


def get_waiting_for_doctor(doctor_id):
    docs = (
        db.collection(WAITING)
        .where(filter=FieldFilter("doctor_id", "==", doctor_id))
        .stream()
    )
    results = []
    for d in docs:
        data    = d.to_dict()
        patient = _get_patient_data(data["patient_id"])
        results.append({
            "id":           d.id,
            "patient_name": patient.get("name", "Unknown"),
            "appt_date":    data["appt_date"],
            "time_slot":    data["time_slot"],
            "reason":       data["reason"],
        })
    return sorted(results, key=lambda x: (x["appt_date"], x["time_slot"]))


def get_waiting_for_patient(patient_id):
    docs = (
        db.collection(WAITING)
        .where(filter=FieldFilter("patient_id", "==", patient_id))
        .stream()
    )
    results = []
    for d in docs:
        data   = d.to_dict()
        doctor = _get_doctor_data(data["doctor_id"])
        results.append({
            "id":             d.id,
            "doctor_name":    doctor.get("name", "Unknown"),
            "specialization": doctor.get("specialization", ""),
            "appt_date":      data["appt_date"],
            "time_slot":      data["time_slot"],
            "reason":         data["reason"],
        })
    return sorted(results, key=lambda x: (x["appt_date"], x["time_slot"]))
