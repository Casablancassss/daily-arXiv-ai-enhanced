#!/usr/bin/env python3
"""
Send paper recommendation report via Email.
"""

import os
import sys
import argparse

import dotenv

# Load environment variables
if os.path.exists('.env'):
    dotenv.load_dotenv()


def mask_email(email: str) -> str:
    """Mask email address for privacy in logs"""
    if '@' not in email:
        return email
    local, domain = email.split('@', 1)
    # Mask local part
    if len(local) <= 2:
        masked_local = '*' * len(local)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    return f"{masked_local}@{domain}"


def summarize_recipients(emails: list) -> str:
    """Summarize email recipients for logging without exposing PII"""
    if not emails:
        return "0 recipients"
    if len(emails) == 1:
        return f"1 recipient ({mask_email(emails[0])})"
    domains = set(e.split('@')[1] if '@' in e else 'unknown' for e in emails)
    return f"{len(emails)} recipients (domains: {', '.join(sorted(domains))})"


def send_email(
    smtp_server: str,
    smtp_port: int,
    username: str,
    password: str,
    from_addr: str,
    to_addrs: list,
    subject: str,
    body: str
) -> bool:
    """Send email via SMTP"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_addr
        msg['To'] = ', '.join(to_addrs)

        # Plain text and HTML versions
        text_body = body.replace('**', '').replace('##', '#').replace('\n\n', '\n')
        html_body = body.replace('\n', '<br>')

        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))

        # Default SMTP timeout is 60 seconds
        smtp_timeout = int(os.environ.get('SMTP_TIMEOUT', '60'))
        with smtplib.SMTP(smtp_server, smtp_port, timeout=smtp_timeout) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(from_addr, to_addrs, msg.as_string())

        return True
    except Exception as e:
        print(f"Email send failed: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Send paper recommendation report via email")
    parser.add_argument("--report", type=str, required=True, help="Report file to send")
    parser.add_argument("--email-to", type=str, required=True, help="Email recipient (comma-separated)")
    parser.add_argument("--subject", type=str, default="Daily arXiv Paper Recommendations", help="Email subject")
    args = parser.parse_args()

    # Read report
    try:
        with open(args.report, "r", encoding="utf-8") as f:
            report_content = f.read()
    except FileNotFoundError:
        print(f"Error: Report file not found: {args.report}", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error reading report file: {e}", file=sys.stderr)
        sys.exit(1)

    if not report_content.strip():
        print("Report is empty, skipping send")
        sys.exit(1)

    # Get SMTP configuration
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port_str = os.environ.get('SMTP_PORT', '587')

    # Safely parse SMTP port
    try:
        smtp_port = int(smtp_port_str)
    except ValueError:
        print(f"Warning: Invalid SMTP_PORT '{smtp_port_str}', using default 587", file=sys.stderr)
        smtp_port = 587

    smtp_user = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    from_addr = os.environ.get('SMTP_FROM', smtp_user)

    if not all([smtp_server, smtp_user, smtp_password]):
        print("Error: SMTP not configured. Please set SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD environment variables.", file=sys.stderr)
        sys.exit(1)

    # Send email - filter out empty addresses
    to_addrs = [e.strip() for e in args.email_to.split(',') if e.strip()]
    if not to_addrs:
        print("Error: No valid email addresses provided", file=sys.stderr)
        sys.exit(1)
    # Use masked summary for logging to protect PII
    print(f"Sending to email: {summarize_recipients(to_addrs)}...")
    if send_email(
        smtp_server, smtp_port, smtp_user, smtp_password,
        from_addr, to_addrs, args.subject, report_content
    ):
        print("Email sent successfully")
    else:
        print("Failed to send email")
        sys.exit(1)


if __name__ == "__main__":
    main()
