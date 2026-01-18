
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
import pandas as pd
import html

import utils.db as db
from utils.secrets import get_secret


# --- SMTP CONFIG ---
HOST = "smtp.gmail.com"
PORT = 465
context = ssl.create_default_context()

# --- SECRETS ---
username = get_secret("EMAIL_USERNAME", section="em")
password = get_secret("EMAIL_PASSWORD", section="em")
receiver = get_secret("EMAIL_RECEIVER", section="em")

if not username or not password or not receiver:
    raise ValueError("Missing required ENV: EMAIL_USERNAME, EMAIL_PASSWORD, EMAIL_RECEIVER")

APP_URL = "https://ebistf.streamlit.app/"


def build_plain_text_body(task_list):
    today = date.today().strftime("%Y-%m-%d")
    lines = [f"Today's task list — {today}", "", "Tasks:"]
    if not task_list:
        lines.append("- No tasks for today.")
    else:
        for t in task_list:
            story_id = t.get("story_id") or "-"
            story_name = t.get("story_name") or "-"
            task_id = t.get("task_id") or "-"
            task_name = t.get("task_name") or "-"
            estimate_date = t.get("estimate_date") or "-"
            lines.append(f"- [{story_id}] {story_name} | ({task_id}) {task_name} | Due: {estimate_date}")
    lines.append("")
    lines.append(f"Open application: {APP_URL}")
    lines.append("This email was generated automatically. Please do not reply.")
    return "\n".join(lines)


def build_html_body(task_list):
    """Enterprise-grade HTML email with inline CSS (Outlook/Gmail friendly) and CTA link."""
    today = date.today().strftime("%Y-%m-%d")
    total = len(task_list)
    safe_url = html.escape(APP_URL, quote=True)

    # Header + opening
    body = f"""\
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Today's Task List</title>
</head>
<body style="margin:0; padding:20px; background-color:#f5f7fa; font-family: Arial, Helvetica, sans-serif;">
  <div style="max-width:720px; margin:0 auto; background-color:#ffffff; border:1px solid #e1e5ea; border-radius:8px; padding:24px;">
    
    <!-- HEADER -->
    <div style="display:block; margin-bottom:16px;">
      <h2 style="margin:0 0 8px 0; font-size:22px; color:#1a1f36;">Today's Task List</h2>
      <div style="font-size:13px; color:#6b7280;">Date: {today} • Total tasks: {total}</div>
    </div>

    <p style="color:#4a4f5e; font-size:14px; line-height:1.6; margin:16px 0 12px;">
      Below are the tasks scheduled for today.
    </p>

    <!-- CTA BUTTON (bulletproof) -->
    <table role="presentation" border="0" cellspacing="0" cellpadding="0" style="margin: 8px 0 16px 0;">
      <tr>
        <td align="left" bgcolor="#2563EB" style="border-radius:6px;">
          <a href="{safe_url}" 
             style="display:inline-block; padding:10px 16px; font-size:14px; color:#ffffff; text-decoration:none; 
                    font-weight:600; font-family:Arial, Helvetica, sans-serif; border-radius:6px; background-color:#2563EB;"
             target="_blank" rel="noopener">
             Open Application
          </a>
        </td>
      </tr>
    </table>

    <!-- TABLE -->
    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="width:100%; border-collapse:collapse; margin-top:12px;">
      <thead>
        <tr>
          <th align="left" style="background:#f0f2f5; color:#1f2937; padding:10px; border:1px solid #d8dde6; font-size:13px;">Story ID</th>
          <th align="left" style="background:#f0f2f5; color:#1f2937; padding:10px; border:1px solid #d8dde6; font-size:13px;">Story Name</th>
          <th align="left" style="background:#f0f2f5; color:#1f2937; padding:10px; border:1px solid #d8dde6; font-size:13px;">Task ID</th>
          <th align="left" style="background:#f0f2f5; color:#1f2937; padding:10px; border:1px solid #d8dde6; font-size:13px;">Task Name</th>
          <th align="left" style="background:#f0f2f5; color:#1f2937; padding:10px; border:1px solid #d8dde6; font-size:13px;">Due Date</th>
        </tr>
      </thead>
      <tbody>
"""

    # Rows
    for idx, task in enumerate(task_list):
        # Escape values for safe HTML
        story_id = html.escape(str(task.get("story_id") or "-"))
        story_name = html.escape(str(task.get("story_name") or "-"))
        task_id = html.escape(str(task.get("task_id") or "-"))
        task_name = html.escape(str(task.get("task_name") or "-"))
        estimate_date = html.escape(str(task.get("estimate_date") or "-"))

        # Optional zebra striping
        row_bg = "#ffffff" if idx % 2 == 0 else "#fafbfc"

        body += f"""\
        <tr style="background-color:{row_bg};">
          <td style="padding:8px 10px; border:1px solid #e1e5ea; font-size:13px; color:#111827;">{story_id}</td>
          <td style="padding:8px 10px; border:1px solid #e1e5ea; font-size:13px; color:#111827;">{story_name}</td>
          <td style="padding:8px 10px; border:1px solid #e1e5ea; font-size:13px; color:#111827;">{task_id}</td>
          <td style="padding:8px 10px; border:1px solid #e1e5ea; font-size:13px; color:#111827;">{task_name}</td>
          <td style="padding:8px 10px; border:1px solid #e1e5ea; font-size:13px; color:#111827;">{estimate_date}</td>
        </tr>
"""

    # Closing
    body += f"""\
      </tbody>
    </table>

    <!-- SECONDARY LINK (text) -->
    <p style="margin:16px 0 0; font-size:13px; color:#374151;">
      Or open the application directly: 
      <a href="{safe_url}" style="color:#2563EB; text-decoration:underline;" target="_blank" rel="noopener">{safe_url}</a>
    </p>

    <!-- FOOTER -->
    <p style="color:#6b7280; font-size:12px; margin-top:24px;">
      This email was generated automatically. Please do not reply.
    </p>
  </div>
</body>
</html>
"""
    return body


def send_email(task_list, receiver_email):
    # Subject with date
    subject = f"Today's Task List — {date.today().strftime('%Y-%m-%d')}"

    # Use multipart/alternative (plain text + HTML)
    message = MIMEMultipart("alternative")
    message["From"] = username
    message["To"] = receiver_email
    message["Subject"] = subject

    plain = build_plain_text_body(task_list)
    html_body = build_html_body(task_list)

    # Attach parts (plain first, then HTML)
    message.attach(MIMEText(plain, "plain", "utf-8"))
    message.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP_SSL(HOST, PORT, context=context) as server:
        server.login(username, password)
        server.send_message(message)


def get_tasks_from_db():
    """Fetch tasks from DB view {schema}.task_for_today, cast to strings."""
    conn = db.pg_conn()
    try:
        query = f"SELECT * FROM {db.schema()}.task_for_today;"
        db_tasks = pd.read_sql_query(query, conn, dtype=str)
    finally:
        try:
            conn.close()
        except Exception:
            pass

    tasks = []
    for _, row in db_tasks.iterrows():
        tasks.append({
            "story_id": row.get("story_id"),
            "story_name": row.get("story_name"),
            "task_id": row.get("task_id"),
            "task_name": row.get("task_name"),
            "estimate_date": row.get("estimate_date")
        })
    return tasks


def main():
    tasks = get_tasks_from_db()
    if tasks:
        send_email(tasks, receiver)
    else:
        print("No tasks to send.")


if __name__ == "__main__":
    main()
