"""
utils/email_service.py
─────────────────────
Centralised email notification service for MediBook.

All email logic lives here — routes never build email content directly.
Each public function maps to one real-world event:

  send_booking_confirmation_to_patient()  → appointment confirmed
  send_booking_email_to_doctor()          → doctor notified of new booking
  send_waiting_list_email()               → patient added to waiting list
  send_approval_request_to_doctor()       → doctor must approve future booking
  send_final_confirmation_email()         → patient confirmed from waiting list

Design principles:
  • Every function is self-contained — pass in plain dicts, get email sent.
  • Failures are caught and logged — a broken SMTP config never crashes a booking.
  • mail (Flask-Mail instance) is injected at call time via current_app, so this
    module has zero circular-import risk with app.py.
"""

from flask import current_app
from flask_mail import Message


# ── Internal helper ───────────────────────────────────────────────────────────

def _send(subject: str, recipients: list[str], html_body: str) -> None:
    """
    Low-level send wrapper.
    Catches ALL exceptions so a broken SMTP config never crashes a booking.
    Logs the error to Flask's logger instead.
    """
    try:
        mail = current_app.extensions["mail"]   # grab the Mail instance Flask registered
        msg  = Message(
            subject    = subject,
            recipients = recipients,            # list of email strings
            html       = html_body,
        )
        mail.send(msg)
    except Exception as exc:
        # Log but never raise — email is a side-effect, not the main transaction
        current_app.logger.error(f"[EmailService] Failed to send '{subject}' → {exc}")


# ── Shared HTML wrapper ───────────────────────────────────────────────────────
# Keeps all emails visually consistent without a template engine dependency.

def _wrap(title: str, colour: str, body_html: str) -> str:
    """Wrap email body in a clean, minimal HTML shell."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"/></head>
    <body style="margin:0;padding:0;background:#f4f6fb;font-family:Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td align="center" style="padding:40px 20px;">
            <table width="600" cellpadding="0" cellspacing="0"
                   style="background:#ffffff;border-radius:12px;overflow:hidden;
                          box-shadow:0 4px 20px rgba(0,0,0,0.08);">

              <!-- Header -->
              <tr>
                <td style="background:{colour};padding:28px 36px;">
                  <h1 style="margin:0;color:#ffffff;font-size:22px;">🏥 MediBook</h1>
                  <p  style="margin:6px 0 0;color:rgba(255,255,255,0.85);font-size:14px;">
                    Hospital Appointment System
                  </p>
                </td>
              </tr>

              <!-- Title bar -->
              <tr>
                <td style="background:{colour}22;padding:16px 36px;
                           border-bottom:3px solid {colour};">
                  <h2 style="margin:0;color:{colour};font-size:18px;">{title}</h2>
                </td>
              </tr>

              <!-- Body -->
              <tr>
                <td style="padding:28px 36px;color:#333333;font-size:15px;
                           line-height:1.7;">
                  {body_html}
                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background:#f8f9fa;padding:18px 36px;
                           border-top:1px solid #e9ecef;
                           color:#6c757d;font-size:12px;text-align:center;">
                  This is an automated message from MediBook. Please do not reply.
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """


def _info_row(label: str, value: str) -> str:
    """Render a single label-value row inside an info table."""
    return f"""
    <tr>
      <td style="padding:10px 16px;font-weight:bold;color:#555;
                 background:#f8f9fa;width:40%;border-bottom:1px solid #e9ecef;">
        {label}
      </td>
      <td style="padding:10px 16px;color:#333;
                 background:#ffffff;border-bottom:1px solid #e9ecef;">
        {value}
      </td>
    </tr>
    """


def _info_table(*rows: str) -> str:
    """Wrap label-value rows in a styled table."""
    return f"""
    <table width="100%" cellpadding="0" cellspacing="0"
           style="border:1px solid #e9ecef;border-radius:8px;
                  overflow:hidden;margin:16px 0;">
      {''.join(rows)}
    </table>
    """


def _status_badge(text: str, colour: str) -> str:
    return f"""
    <span style="display:inline-block;padding:6px 16px;border-radius:20px;
                 background:{colour};color:#fff;font-weight:bold;font-size:13px;">
      {text}
    </span>
    """


# ── 1. Booking confirmed → Patient ────────────────────────────────────────────

def send_booking_confirmation_to_patient(
    patient_email: str,
    patient_name:  str,
    doctor_name:   str,
    specialization: str,
    appt_date:     str,
    time_slot:     str,
) -> None:
    """
    Sent immediately when a booking is confirmed (no waiting list).
    Tells the patient: who, when, where.
    """
    body = f"""
    <p>Dear <strong>{patient_name}</strong>,</p>
    <p>
      Your appointment has been <strong>confirmed</strong> successfully.
      Please find the details below:
    </p>

    {_info_table(
        _info_row("Doctor",         f"Dr. {doctor_name}"),
        _info_row("Specialization", specialization),
        _info_row("Date",           appt_date),
        _info_row("Time Slot",      time_slot),
        _info_row("Status",         _status_badge("✅ Confirmed", "#198754")),
    )}

    <p>
      Please arrive <strong>10 minutes early</strong> and carry a valid ID.
      If you need to cancel, please do so at least 2 hours in advance.
    </p>
    <p>We wish you good health! 💙</p>
    """
    _send(
        subject    = "✅ Appointment Confirmed — MediBook",
        recipients = [patient_email],
        html_body  = _wrap("Appointment Confirmed", "#198754", body),
    )


# ── 2. New booking → Doctor ───────────────────────────────────────────────────

def send_booking_email_to_doctor(
    doctor_email:  str,
    doctor_name:   str,
    patient_name:  str,
    appt_date:     str,
    time_slot:     str,
) -> None:
    """
    Sent to the doctor when a patient books a confirmed appointment.
    Keeps the doctor's schedule up to date.
    """
    body = f"""
    <p>Dear <strong>Dr. {doctor_name}</strong>,</p>
    <p>
      A new appointment has been booked with you.
      Please review the details:
    </p>

    {_info_table(
        _info_row("Patient",   patient_name),
        _info_row("Date",      appt_date),
        _info_row("Time Slot", time_slot),
        _info_row("Status",    _status_badge("✅ Confirmed", "#198754")),
    )}

    <p>
      Please log in to <strong>MediBook</strong> to view your full schedule.
    </p>
    """
    _send(
        subject    = f"📅 New Appointment — {patient_name} on {appt_date}",
        recipients = [doctor_email],
        html_body  = _wrap("New Appointment Booked", "#0d6efd", body),
    )


# ── 3. Slot taken → Patient added to waiting list ─────────────────────────────

def send_waiting_list_email(
    patient_email: str,
    patient_name:  str,
    doctor_name:   str,
    specialization: str,
    appt_date:     str,
    time_slot:     str,
) -> None:
    """
    Sent when the requested slot is already taken.
    Patient is on the waiting list and will be auto-promoted on cancellation.
    """
    body = f"""
    <p>Dear <strong>{patient_name}</strong>,</p>
    <p>
      The slot you requested is currently <strong>fully booked</strong>.
      You have been added to the <strong>waiting list</strong> and will be
      automatically confirmed if a cancellation occurs.
    </p>

    {_info_table(
        _info_row("Doctor",         f"Dr. {doctor_name}"),
        _info_row("Specialization", specialization),
        _info_row("Date",           appt_date),
        _info_row("Time Slot",      time_slot),
        _info_row("Status",         _status_badge("🕐 Waiting List", "#fd7e14")),
    )}

    <p>
      You will receive another email as soon as your appointment is confirmed.
      No action is required from your side right now.
    </p>
    """
    _send(
        subject    = "🕐 Added to Waiting List — MediBook",
        recipients = [patient_email],
        html_body  = _wrap("Added to Waiting List", "#fd7e14", body),
    )


# ── 4. Future date booking → Doctor approval required ────────────────────────

def send_approval_request_to_doctor(
    doctor_email:  str,
    doctor_name:   str,
    patient_name:  str,
    appt_date:     str,
    time_slot:     str,
) -> None:
    """
    Sent when a patient books more than 2 days ahead.
    Doctor must log in and manually confirm the appointment.
    """
    body = f"""
    <p>Dear <strong>Dr. {doctor_name}</strong>,</p>
    <p>
      A patient has requested an appointment that is
      <strong>more than 2 days ahead</strong>.
      This requires your <strong>manual approval</strong> before it is confirmed.
    </p>

    {_info_table(
        _info_row("Patient",   patient_name),
        _info_row("Date",      appt_date),
        _info_row("Time Slot", time_slot),
        _info_row("Status",    _status_badge("📋 Awaiting Your Approval", "#0dcaf0")),
    )}

    <p>
      Please log in to <strong>MediBook → Waiting List</strong> and click
      <strong>Confirm</strong> to approve this appointment.
    </p>
    """
    _send(
        subject    = f"📋 Approval Required — {patient_name} on {appt_date}",
        recipients = [doctor_email],
        html_body  = _wrap("Appointment Approval Required", "#0dcaf0", body),
    )


def send_future_date_pending_to_patient(
    patient_email:  str,
    patient_name:   str,
    doctor_name:    str,
    specialization: str,
    appt_date:      str,
    time_slot:      str,
) -> None:
    """
    Sent to the patient when their future-date booking is pending doctor approval.
    """
    body = f"""
    <p>Dear <strong>{patient_name}</strong>,</p>
    <p>
      Your appointment request has been received. Since the date is
      <strong>more than 2 days ahead</strong>, it requires
      <strong>doctor approval</strong> before it is confirmed.
    </p>

    {_info_table(
        _info_row("Doctor",         f"Dr. {doctor_name}"),
        _info_row("Specialization", specialization),
        _info_row("Date",           appt_date),
        _info_row("Time Slot",      time_slot),
        _info_row("Status",         _status_badge("📋 Pending Doctor Approval", "#0dcaf0")),
    )}

    <p>
      You will receive a confirmation email once the doctor approves your request.
      No action is required from your side right now.
    </p>
    """
    _send(
        subject    = "📋 Appointment Pending Approval — MediBook",
        recipients = [patient_email],
        html_body  = _wrap("Appointment Pending Approval", "#0dcaf0", body),
    )


# ── 5. Doctor confirms waiting list entry → Patient ──────────────────────────

def send_final_confirmation_email(
    patient_email:  str,
    patient_name:   str,
    doctor_name:    str,
    specialization: str,
    appt_date:      str,
    time_slot:      str,
) -> None:
    """
    Sent when a doctor manually confirms a future_date waiting list entry,
    OR when a patient is auto-promoted after a cancellation.
    This is the patient's final "you're in" email.
    """
    body = f"""
    <p>Dear <strong>{patient_name}</strong>,</p>
    <p>
      Great news! 🎉 Your appointment has been
      <strong>officially confirmed</strong>.
    </p>

    {_info_table(
        _info_row("Doctor",         f"Dr. {doctor_name}"),
        _info_row("Specialization", specialization),
        _info_row("Date",           appt_date),
        _info_row("Time Slot",      time_slot),
        _info_row("Status",         _status_badge("✅ Confirmed", "#198754")),
    )}

    <p>
      Please arrive <strong>10 minutes early</strong> and carry a valid ID.
      If you need to cancel, please do so at least 2 hours in advance via MediBook.
    </p>
    <p>We look forward to seeing you. Stay healthy! 💙</p>
    """
    _send(
        subject    = "🎉 Appointment Confirmed — MediBook",
        recipients = [patient_email],
        html_body  = _wrap("Your Appointment is Confirmed!", "#198754", body),
    )
