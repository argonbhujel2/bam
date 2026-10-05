"""Transactional email helpers with branded HTML + inline logo."""
import os
from flask import current_app
from flask_mail import Message
from app import mail


def mail_configured():
    server = current_app.config.get("MAIL_SERVER")
    user = current_app.config.get("MAIL_USERNAME")
    password = current_app.config.get("MAIL_PASSWORD")
    ok = bool(server and user and password)
    if not ok:
        current_app.logger.warning(
            "Mail incomplete — need MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD in .env"
        )
    return ok


def _logo_path():
    """Filesystem path to logo.png for CID embed."""
    root = current_app.root_path
    path = os.path.join(root, "static", "images", "logo.png")
    if os.path.isfile(path):
        return path
    return None


def _brand_html(title, intro, rows, footer_note=None, use_cid_logo=True):
    logo_src = "cid:bam_logo" if use_cid_logo and _logo_path() else ""
    logo_block = ""
    if logo_src:
        logo_block = f'''
        <tr>
          <td align="center" style="padding:32px 24px 8px;">
            <img src="{logo_src}" alt="BAM Studio" width="80" height="80"
                 style="display:block;border-radius:50%;border:0;outline:none;
                        width:80px;height:80px;" />
          </td>
        </tr>'''
    else:
        logo_block = '''
        <tr>
          <td align="center" style="padding:32px 24px 8px;">
            <div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#0077b6,#6d28d9);
                        color:#fff;font-size:22px;font-weight:700;line-height:80px;margin:0 auto;">BAM</div>
          </td>
        </tr>'''

    rows_html = ""
    for label, value in rows:
        if value is None or str(value).strip() == "":
            value = "—"
        value = (
            str(value)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br>")
        )
        label = str(label).replace("&", "&amp;")
        rows_html += f'''
        <tr>
          <td style="padding:12px 0;border-bottom:1px solid #eef1f6;vertical-align:top;width:34%;">
            <span style="font-size:11px;letter-spacing:0.08em;text-transform:uppercase;color:#8a94a6;font-weight:600;">{label}</span>
          </td>
          <td style="padding:12px 0 12px 16px;border-bottom:1px solid #eef1f6;color:#0a1020;font-size:15px;line-height:1.55;">
            {value}
          </td>
        </tr>'''

    footer = footer_note or "This message was sent from the BAM Studio website."
    title_esc = str(title).replace("&", "&amp;")
    intro_esc = str(intro).replace("&", "&amp;")

    return f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#eef1f8;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#eef1f8;padding:40px 16px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
               style="max-width:560px;background:#ffffff;border-radius:16px;overflow:hidden;
                      box-shadow:0 12px 40px rgba(15,30,60,0.1);">
          <tr>
            <td style="height:5px;background:linear-gradient(90deg,#0077b6,#6d28d9);font-size:0;line-height:0;">&nbsp;</td>
          </tr>
          {logo_block}
          <tr>
            <td align="center" style="padding:4px 28px 8px;">
              <div style="font-size:20px;font-weight:700;letter-spacing:-0.03em;color:#0a1020;">BAM Studio</div>
              <div style="font-size:13px;color:#7a8499;margin-top:6px;">Digital Experiences. Engineered.</div>
            </td>
          </tr>
          <tr>
            <td style="padding:24px 28px 8px;">
              <div style="font-size:22px;font-weight:700;color:#0a1020;letter-spacing:-0.02em;">{title_esc}</div>
              <div style="font-size:14px;color:#4a5568;margin-top:10px;line-height:1.55;">{intro_esc}</div>
            </td>
          </tr>
          <tr>
            <td style="padding:12px 28px 28px;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
                     style="background:#f7f8fc;border-radius:12px;padding:4px 16px;">
                <tr><td style="padding:8px 16px;">
                  <table role="presentation" width="100%" cellspacing="0" cellpadding="0">
                    {rows_html}
                  </table>
                </td></tr>
              </table>
            </td>
          </tr>
          <tr>
            <td style="padding:8px 28px 32px;">
              <div style="font-size:12px;color:#7a8499;line-height:1.55;">{footer}</div>
              <div style="font-size:11px;color:#a0aec0;margin-top:16px;">
                © BAM Studio · Founded by Argon Bhujel
              </div>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>'''


def _plain_from_rows(title, rows):
    lines = [title, ""]
    for label, value in rows:
        lines.append(f"{label}: {value if value not in (None, '') else '—'}")
    return "\n".join(lines)


def _attach_logo(msg):
    path = _logo_path()
    if not path:
        return
    try:
        with open(path, "rb") as f:
            data = f.read()
        msg.attach(
            "logo.png",
            "image/png",
            data,
            "inline",
            headers={"Content-ID": "<bam_logo>"},
        )
    except Exception as e:
        current_app.logger.error("Logo attach failed: %s", e)


def send_notification(subject, body_text, html_body=None, recipients=None, reply_to=None):
    if not mail_configured():
        current_app.logger.info("Mail not configured — skipping: %s", subject)
        return False
    if not recipients:
        to = current_app.config.get("MAIL_NOTIFY_TO")
        if not to:
            try:
                from app.utils.helpers import get_setting
                to = get_setting("email", "") or None
            except Exception:
                to = None
        if not to:
            to = current_app.config.get("MAIL_DEFAULT_SENDER")
        recipients = [to] if to else []
    if not recipients:
        return False
    try:
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            body=body_text,
            html=html_body,
            sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
        )
        if reply_to:
            msg.reply_to = reply_to
        _attach_logo(msg)
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error("Email send failed: %s", e)
        return False


def send_confirmation_to_user(to_email, name, kind="inquiry"):
    """Auto-reply to the person who submitted the form."""
    if not to_email:
        return False
    name = name or "there"
    if kind == "application":
        title = "We received your application"
        intro = (
            f"Hi {name}, thank you for applying to BAM Studio. "
            "Our team will review your application and get back to you if there is a match."
        )
        subject = "[BAM Studio] Application received"
    elif kind == "contact":
        title = "We received your message"
        intro = (
            f"Hi {name}, thank you for contacting BAM Studio. "
            "We have received your message and will reply as soon as we can."
        )
        subject = "[BAM Studio] Message received"
    else:
        title = "We received your project inquiry"
        intro = (
            f"Hi {name}, thank you for your interest in working with BAM Studio. "
            "We have received your project inquiry and will review it shortly."
        )
        subject = "[BAM Studio] Inquiry received"

    rows = [
        ("Status", "Received"),
        ("Next step", "Our team will follow up by email"),
    ]
    html = _brand_html(
        title,
        intro,
        rows,
        "If you did not submit this form, you can ignore this email.",
    )
    text = f"{title}\n\n{intro}\n"
    return send_notification(subject, text, html, recipients=[to_email])


def notify_project_inquiry(inq):
    rows = [
        ("Name", inq.name),
        ("Email", inq.email),
        ("Phone", inq.phone),
        ("Company", inq.company),
        ("Project type", inq.project_type),
        ("Budget", inq.budget),
        ("Message", inq.message),
    ]
    html = _brand_html(
        "New project inquiry",
        "Someone submitted a project inquiry on the BAM Studio website.",
        rows,
        "Reply directly to the applicant email, or review in Admin → Inquiries.",
    )
    text = _plain_from_rows("New project inquiry", rows)
    ok = send_notification(
        f"[BAM Studio] Project inquiry — {inq.name}",
        text,
        html,
        reply_to=inq.email,
    )
    try:
        send_confirmation_to_user(inq.email, inq.name, kind="inquiry")
    except Exception as e:
        current_app.logger.error("Confirmation email failed: %s", e)
    return ok


def notify_contact_message(msg_obj):
    rows = [
        ("Name", msg_obj.name),
        ("Email", msg_obj.email),
        ("Phone", msg_obj.phone),
        ("Subject", msg_obj.subject),
        ("Message", msg_obj.message),
    ]
    html = _brand_html(
        "New contact message",
        "A general message was sent from the BAM Studio contact form.",
        rows,
        "Reply to the sender email, or open Admin → Inquiries.",
    )
    text = _plain_from_rows("New contact message", rows)
    ok = send_notification(
        f"[BAM Studio] Contact — {msg_obj.name}",
        text,
        html,
        reply_to=msg_obj.email,
    )
    try:
        send_confirmation_to_user(msg_obj.email, msg_obj.name, kind="contact")
    except Exception as e:
        current_app.logger.error("Confirmation email failed: %s", e)
    return ok


def notify_career_application(app_obj):
    job = app_obj.career.title_en if app_obj.career else "Position"
    rows = [
        ("Position", job),
        ("Name", app_obj.full_name),
        ("Email", app_obj.email),
        ("Phone", app_obj.phone),
        ("Experience", app_obj.experience),
        ("Portfolio", app_obj.portfolio_url),
        ("GitHub", app_obj.github_url),
        ("LinkedIn", app_obj.linkedin_url),
        ("CV", app_obj.cv_url),
        ("Cover message", app_obj.cover_message),
    ]
    html = _brand_html(
        "New job application",
        f'A candidate applied for "{job}" via the BAM Studio careers page.',
        rows,
        "Review the CV and status in Admin → Applications.",
    )
    text = _plain_from_rows(f"New job application — {job}", rows)
    ok = send_notification(
        f"[BAM Studio] Application — {job} — {app_obj.full_name}",
        text,
        html,
        reply_to=app_obj.email,
    )
    try:
        send_confirmation_to_user(app_obj.email, app_obj.full_name, kind="application")
    except Exception as e:
        current_app.logger.error("Confirmation email failed: %s", e)
    return ok


def notify_status_update(kind, name, email, old_status, new_status, extra=""):
    """Email user when admin changes application / inquiry status."""
    if not email or old_status == new_status:
        return False
    rows = [
        ("Name", name),
        ("Previous status", old_status or "—"),
        ("New status", new_status),
    ]
    if extra:
        rows.append(("Note", extra))
    if kind == "application":
        title = "Application status updated"
        intro = f"Hi {name}, your job application status at BAM Studio has been updated."
        subject = f"[BAM Studio] Application status: {new_status}"
    elif kind == "contact":
        title = "Message status updated"
        intro = f"Hi {name}, your contact message status has been updated."
        subject = f"[BAM Studio] Message status: {new_status}"
    else:
        title = "Inquiry status updated"
        intro = f"Hi {name}, your project inquiry status has been updated."
        subject = f"[BAM Studio] Inquiry status: {new_status}"
    html = _brand_html(title, intro, rows, "If you have questions, reply to this email.")
    text = _plain_from_rows(title, rows)
    return send_notification(subject, text, html, recipients=[email])
