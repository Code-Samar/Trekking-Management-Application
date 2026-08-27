import os
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

import requests
from flask import current_app

from extensions import celery_app as celery, db
from models import User, Trek, Booking


# ---------------------------------------------------------------------------
# Notification helpers
# ---------------------------------------------------------------------------

def _send_email(to_email, subject, html_body):
    cfg = current_app.config
    if not cfg.get("MAIL_ENABLED") or not cfg.get("MAIL_USERNAME"):
        # Dev fallback: log instead of sending, so the app is fully runnable
        # locally without real SMTP credentials.
        print(f"[MAIL:DEV-MODE] To={to_email} Subject={subject}\n{html_body[:300]}...")
        return True
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = cfg["MAIL_USERNAME"]
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(cfg["MAIL_SERVER"], cfg["MAIL_PORT"]) as server:
            server.starttls()
            server.login(cfg["MAIL_USERNAME"], cfg["MAIL_PASSWORD"])
            server.sendmail(cfg["MAIL_USERNAME"], [to_email], msg.as_string())
        return True
    except Exception as exc:
        print(f"[MAIL:ERROR] Could not send to {to_email}: {exc}")
        return False


def _send_gchat_webhook(webhook_url, text):
    if not webhook_url:
        print(f"[GCHAT:DEV-MODE] {text[:200]}...")
        return True
    try:
        requests.post(webhook_url, json={"text": text}, timeout=10)
        return True
    except Exception as exc:
        print(f"[GCHAT:ERROR] {exc}")
        return False


# ---------------------------------------------------------------------------
# a) Scheduled: Daily reminders for upcoming treks
# ---------------------------------------------------------------------------

@celery.task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    tomorrow = (datetime.utcnow() + timedelta(minute="*")).date()
    upcoming_treks = Trek.query.filter(Trek.start_date == tomorrow, Trek.status == "Open").all()

    sent = 0
    for trek in upcoming_treks:
        bookings = Booking.query.filter_by(trek_id=trek.id, status="Booked").all()
        for b in bookings:
            user = User.query.get(b.user_id)
            if not user:
                continue
            subject = f"Reminder: {trek.name} starts tomorrow!"
            body = (
                f"<h3>Hi {user.name},</h3>"
                f"<p>This is a reminder that your trek <b>{trek.name}</b> "
                f"({trek.location}) starts on <b>{trek.start_date}</b>.</p>"
                f"<p>Duration: {trek.duration_days} days | Difficulty: {trek.difficulty}</p>"
                f"<p>Please carry appropriate gear and arrive on time. Happy trekking!</p>"
            )
            _send_email(user.email, subject, body)
            _send_gchat_webhook(
                os.environ.get("TMA_GCHAT_WEBHOOK", ""),
                f"Reminder sent to {user.name} for trek '{trek.name}' starting {trek.start_date}",
            )
            sent += 1

    print(f"[TASK] send_daily_reminders complete. Reminders sent: {sent}")
    return {"reminders_sent": sent, "treks_checked": len(upcoming_treks)}


# ---------------------------------------------------------------------------
# b) Scheduled: Monthly activity report for Admin
# ---------------------------------------------------------------------------

@celery.task(name="tasks.send_monthly_report")
def send_monthly_report():
    now = datetime.utcnow()
    first_of_this_month = now.replace(day=1)
    last_month_end = first_of_this_month - timedelta(days=1)
    first_of_last_month = last_month_end.replace(day=1)

    treks_conducted = Trek.query.filter(
        Trek.status == "Completed",
        Trek.end_date >= first_of_last_month.date(),
        Trek.end_date <= last_month_end.date(),
    ).all()

    bookings_last_month = Booking.query.filter(
        Booking.booking_date >= first_of_last_month,
        Booking.booking_date <= last_month_end,
    ).all()
    participant_ids = {b.user_id for b in bookings_last_month}

    popularity = {}
    for b in bookings_last_month:
        popularity[b.trek_id] = popularity.get(b.trek_id, 0) + 1
    popular_treks = sorted(popularity.items(), key=lambda x: x[1], reverse=True)[:5]
    popular_rows = ""
    for trek_id, count in popular_treks:
        trek = Trek.query.get(trek_id)
        if trek:
            popular_rows += f"<tr><td>{trek.name}</td><td>{trek.location}</td><td>{count}</td></tr>"

    html = f"""
    <html><body style="font-family:Arial,sans-serif;">
      <h2>Monthly Trekking Activity Report — {first_of_last_month.strftime('%B %Y')}</h2>
      <p><b>Treks Conducted:</b> {len(treks_conducted)}</p>
      <p><b>Users Participated:</b> {len(participant_ids)}</p>
      <p><b>Total Bookings:</b> {len(bookings_last_month)}</p>
      <h3>Most Popular Treks</h3>
      <table border="1" cellpadding="6" cellspacing="0">
        <tr><th>Trek</th><th>Location</th><th>Bookings</th></tr>
        {popular_rows or '<tr><td colspan="3">No bookings recorded</td></tr>'}
      </table>
    </body></html>
    """

    report_dir = current_app.config["REPORT_DIR"]
    os.makedirs(report_dir, exist_ok=True)
    filename = f"monthly_report_{first_of_last_month.strftime('%Y_%m')}.html"
    filepath = os.path.join(report_dir, filename)
    with open(filepath, "w") as f:
        f.write(html)

    admin = User.query.filter_by(role="admin").first()
    if admin:
        _send_email(admin.email, f"TMA Monthly Report — {first_of_last_month.strftime('%B %Y')}", html)

    print(f"[TASK] send_monthly_report complete. Saved to {filepath}")
    return {"report_file": filepath, "treks_conducted": len(treks_conducted), "participants": len(participant_ids)}


# ---------------------------------------------------------------------------
# c) User-triggered async: export booking history as CSV
# ---------------------------------------------------------------------------

@celery.task(name="tasks.export_booking_history_csv")
def export_booking_history_csv(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ValueError("User not found")

    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.booking_date.desc()).all()

    export_dir = current_app.config["EXPORT_DIR"]
    os.makedirs(export_dir, exist_ok=True)
    filename = f"booking_history_user_{user_id}_{int(datetime.utcnow().timestamp())}.csv"
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["User ID", "Trek Name", "Location", "Booking Status", "Booking Date", "Start Date", "End Date"])
        for b in bookings:
            trek = Trek.query.get(b.trek_id)
            writer.writerow([
                user_id,
                trek.name if trek else "",
                trek.location if trek else "",
                b.status,
                b.booking_date.strftime("%Y-%m-%d") if b.booking_date else "",
                trek.start_date if trek and trek.start_date else "",
                trek.end_date if trek and trek.end_date else "",
            ])

    _send_email(
        user.email,
        "Your trekking history export is ready",
        f"<p>Hi {user.name},</p><p>Your booking history CSV export has finished. "
        f"You can download it from your dashboard.</p>",
    )
    print(f"[TASK] export_booking_history_csv complete for user {user_id}: {filepath}")
    return filename
