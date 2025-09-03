import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send(to_email, event_name):
    sender_email = "your-email@example.com"
    sender_password = "your-app-password"  # Use an app password, not your real one
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    subject = "Event Permit Confirmation"
    body = f"""
    Dear applicant,

    Your event "{event_name}" has been successfully submitted to Sunshine Coast Council.

    We will review your application and contact you if further information is needed.

    Thank you for supporting civic engagement.

    Regards,
    Sunshine Council Events Team
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print("✅ Email sent to", to_email)
    except Exception as e:
        print("❌ Email failed:", e)
def send(to_email, event_name):
    """
    Stub: print to console. Wire SMTP/SendGrid later.
    """
    if not to_email:
        return
    print(f"[mail] Confirmation → {to_email}: Your event '{event_name}' was received.")
