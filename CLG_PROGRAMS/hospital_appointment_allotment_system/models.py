import sqlite3
from datetime import date, datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "database.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                username      TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                role          TEXT    NOT NULL CHECK(role IN ('doctor','patient'))
            );

            CREATE TABLE IF NOT EXISTS doctors (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id        INTEGER NOT NULL UNIQUE,
                name           TEXT    NOT NULL,
                specialization TEXT    NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS patients (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL UNIQUE,
                name    TEXT    NOT NULL,
                age     INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS appointments (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id  INTEGER NOT NULL,
                patient_id INTEGER NOT NULL,
                appt_date  TEXT    NOT NULL,
                time_slot  TEXT    NOT NULL,
                FOREIGN KEY (doctor_id)  REFERENCES doctors(id),
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            );

            CREATE TABLE IF NOT EXISTS waiting_list (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                doctor_id  INTEGER NOT NULL,
                patient_id INTEGER NOT NULL,
                appt_date  TEXT    NOT NULL,
                time_slot  TEXT    NOT NULL,
                reason     TEXT    NOT NULL DEFAULT 'slot_taken',
                FOREIGN KEY (doctor_id)  REFERENCES doctors(id),
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            );
        """)


# ── Auth helpers ──────────────────────────────────────────────────────────────

def register_user(username, password, role, extra):
    """
    Create a user + matching doctor/patient profile in one transaction.
    extra = {'name': ..., 'specialization': ...}  for doctor
    extra = {'name': ..., 'age': ...}              for patient
    Returns user_id on success, None if username already taken.
    """
    try:
        with get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                (username, generate_password_hash(password), role)
            )
            user_id = cur.lastrowid

            if role == "doctor":
                conn.execute(
                    "INSERT INTO doctors (user_id, name, specialization) VALUES (?, ?, ?)",
                    (user_id, extra["name"], extra["specialization"])
                )
            else:
                conn.execute(
                    "INSERT INTO patients (user_id, name, age) VALUES (?, ?, ?)",
                    (user_id, extra["name"], int(extra["age"]))
                )
        return user_id
    except sqlite3.IntegrityError:
        return None   # username already exists


def login_user(username, password):
    """
    Verify credentials.
    Returns the user row on success, None on failure.
    """
    with get_connection() as conn:
        user = conn.execute(
            "SELECT * FROM users WHERE username=?", (username,)
        ).fetchone()
    if user and check_password_hash(user["password_hash"], password):
        return user
    return None


def get_user_by_id(user_id):
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()


# ── Doctor helpers ────────────────────────────────────────────────────────────

def get_doctor_by_user(user_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM doctors WHERE user_id=?", (user_id,)
        ).fetchone()


def get_all_doctors(specialization=None):
    with get_connection() as conn:
        if specialization:
            return conn.execute(
                "SELECT * FROM doctors WHERE specialization=?", (specialization,)
            ).fetchall()
        return conn.execute("SELECT * FROM doctors").fetchall()


def get_specializations():
    with get_connection() as conn:
        rows = conn.execute("SELECT DISTINCT specialization FROM doctors").fetchall()
        return [r["specialization"] for r in rows]


# ── Patient helpers ───────────────────────────────────────────────────────────

def get_patient_by_user(user_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM patients WHERE user_id=?", (user_id,)
        ).fetchone()


def get_all_patients():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM patients").fetchall()


# ── Appointment helpers ───────────────────────────────────────────────────────

def is_slot_taken(doctor_id, appt_date, time_slot):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM appointments WHERE doctor_id=? AND appt_date=? AND time_slot=?",
            (doctor_id, appt_date, time_slot)
        ).fetchone()
        return row is not None


def is_future_date(appt_date_str):
    appt_dt = datetime.strptime(appt_date_str, "%Y-%m-%d").date()
    return (appt_dt - date.today()).days > 2


def book_appointment(doctor_id, patient_id, appt_date, time_slot):
    """
    Rules (in order):
      1. Date > today+2  → waiting list, reason='future_date'
      2. Slot taken      → waiting list, reason='slot_taken'
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
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO waiting_list (doctor_id,patient_id,appt_date,time_slot,reason) VALUES (?,?,?,?,?)",
            (doctor_id, patient_id, appt_date, time_slot, reason)
        )


def _insert_appointment(doctor_id, patient_id, appt_date, time_slot):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO appointments (doctor_id,patient_id,appt_date,time_slot) VALUES (?,?,?,?)",
            (doctor_id, patient_id, appt_date, time_slot)
        )


def get_appointments_for_doctor(doctor_id):
    """Doctor sees all appointments assigned to them."""
    with get_connection() as conn:
        return conn.execute("""
            SELECT a.id, p.name AS patient_name, a.appt_date, a.time_slot
            FROM appointments a
            JOIN patients p ON p.id = a.patient_id
            WHERE a.doctor_id = ?
            ORDER BY a.appt_date, a.time_slot
        """, (doctor_id,)).fetchall()


def get_appointments_for_patient(patient_id):
    """Patient sees only their own appointments with doctor name + specialization."""
    with get_connection() as conn:
        return conn.execute("""
            SELECT a.id, d.name AS doctor_name, d.specialization,
                   a.appt_date, a.time_slot
            FROM appointments a
            JOIN doctors d ON d.id = a.doctor_id
            WHERE a.patient_id = ?
            ORDER BY a.appt_date, a.time_slot
        """, (patient_id,)).fetchall()


def cancel_appointment(appointment_id, patient_id=None):
    """
    Cancel appointment.
    If patient_id is given, only cancel if it belongs to that patient (security check).
    Auto-promotes first slot_taken waiting entry.
    """
    with get_connection() as conn:
        query = "SELECT * FROM appointments WHERE id=?"
        params = [appointment_id]
        if patient_id:
            query += " AND patient_id=?"
            params.append(patient_id)

        appt = conn.execute(query, params).fetchone()
        if not appt:
            return False

        conn.execute("DELETE FROM appointments WHERE id=?", (appointment_id,))

        waiting = conn.execute(
            """SELECT * FROM waiting_list
               WHERE doctor_id=? AND appt_date=? AND time_slot=? AND reason='slot_taken'
               ORDER BY id LIMIT 1""",
            (appt["doctor_id"], appt["appt_date"], appt["time_slot"])
        ).fetchone()

        if waiting:
            conn.execute(
                "INSERT INTO appointments (doctor_id,patient_id,appt_date,time_slot) VALUES (?,?,?,?)",
                (waiting["doctor_id"], waiting["patient_id"], waiting["appt_date"], waiting["time_slot"])
            )
            conn.execute("DELETE FROM waiting_list WHERE id=?", (waiting["id"],))

    return True


def confirm_waiting(waiting_id, doctor_id):
    """
    Doctor confirms a future_date waiting entry.
    Security: only the assigned doctor can confirm.
    Returns: 'confirmed' | 'slot_now_taken' | None
    """
    with get_connection() as conn:
        entry = conn.execute(
            "SELECT * FROM waiting_list WHERE id=? AND doctor_id=?",
            (waiting_id, doctor_id)
        ).fetchone()

        if not entry:
            return None

        if is_slot_taken(entry["doctor_id"], entry["appt_date"], entry["time_slot"]):
            conn.execute(
                "UPDATE waiting_list SET reason='slot_taken' WHERE id=?", (waiting_id,)
            )
            return "slot_now_taken"

        conn.execute(
            "INSERT INTO appointments (doctor_id,patient_id,appt_date,time_slot) VALUES (?,?,?,?)",
            (entry["doctor_id"], entry["patient_id"], entry["appt_date"], entry["time_slot"])
        )
        conn.execute("DELETE FROM waiting_list WHERE id=?", (waiting_id,))

    return "confirmed"


def get_waiting_for_doctor(doctor_id):
    """Doctor sees only their own waiting list entries."""
    with get_connection() as conn:
        return conn.execute("""
            SELECT w.id, p.name AS patient_name,
                   w.appt_date, w.time_slot, w.reason
            FROM waiting_list w
            JOIN patients p ON p.id = w.patient_id
            WHERE w.doctor_id = ?
            ORDER BY w.appt_date, w.time_slot, w.id
        """, (doctor_id,)).fetchall()


def get_waiting_for_patient(patient_id):
    """Patient sees only their own waiting list entries."""
    with get_connection() as conn:
        return conn.execute("""
            SELECT w.id, d.name AS doctor_name, d.specialization,
                   w.appt_date, w.time_slot, w.reason
            FROM waiting_list w
            JOIN doctors d ON d.id = w.doctor_id
            WHERE w.patient_id = ?
            ORDER BY w.appt_date, w.time_slot, w.id
        """, (patient_id,)).fetchall()


def get_available_slots(doctor_id, appt_date):
    all_slots = [
        "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
        "11:00 AM", "11:30 AM", "12:00 PM", "02:00 PM",
        "02:30 PM", "03:00 PM", "03:30 PM", "04:00 PM",
    ]
    with get_connection() as conn:
        booked = {
            r["time_slot"] for r in conn.execute(
                "SELECT time_slot FROM appointments WHERE doctor_id=? AND appt_date=?",
                (doctor_id, appt_date)
            ).fetchall()
        }
    return [s for s in all_slots if s not in booked]
