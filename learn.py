from flask import Flask, render_template, request, redirect
import sqlite3
import smtplib
from email.message import EmailMessage

app = Flask(__name__)

# -----------------------------
# CREATE DATABASE
# -----------------------------
def init_db():
    conn = sqlite3.connect("requests.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        description TEXT,
        status TEXT DEFAULT 'Pending'
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------------------
# SUBMIT REQUEST
# -----------------------------
@app.route("/submit", methods=["POST"])
def submit():

    email = request.form.get("email")
    description = request.form.get("description")

    # SAVE TO DATABASE
    conn = sqlite3.connect("requests.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO requests (email, description) VALUES (?, ?)",
        (email, description)
    )

    conn.commit()
    conn.close()

    # SEND EMAIL
    try:

        msg = EmailMessage()
        msg["Subject"] = "New Website Request"
        msg["From"] = EMAIL_USER
        msg["To"] = "kkgadashin@gmail.com"

        msg.set_content(f"""
New Website Request

Client Email:
{email}

Website Description:
{description}
""")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        print("Email sent successfully!")

    except Exception as e:
        print("Email error:", e)

    return redirect("/")


# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@app.route("/admin")
def admin():

    conn = sqlite3.connect("requests.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM requests")

    data = cursor.fetchall()

    conn.close()

    page = "<h1>Client Website Requests</h1>"

    for row in data:

        page += f"""
        <p>
        <b>Client Email:</b> {row[1]} <br>
        <b>Description:</b> {row[2]} <br>
        <b>Status:</b> {row[3]} <br>
        <a href="/complete/{row[0]}">Mark Completed</a>
        </p>
        <hr>
        """

    return page


# -----------------------------
# COMPLETE REQUEST
# -----------------------------
@app.route("/complete/<int:req_id>")
def complete(req_id):

    conn = sqlite3.connect("requests.db")
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE requests SET status='Completed' WHERE id=?",
        (req_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")


# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )