import os
import sqlite3
from datetime import datetime, date
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "database", "sports.db")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "arzosporttracker-secret-key-change-in-production")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    os.makedirs(os.path.join(BASE_DIR, "database"), exist_ok=True)
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            weight REAL,
            height REAL,
            daily_step_goal INTEGER DEFAULT 10000,
            daily_water_goal REAL DEFAULT 2.5,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS running_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            run_date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            duration_seconds INTEGER,
            distance_km REAL,
            avg_speed_kmh REAL,
            calories REAL,
            route_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS water_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            log_date TEXT NOT NULL,
            amount_liters REAL NOT NULL,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS daily_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_date TEXT NOT NULL,
            steps INTEGER DEFAULT 0,
            distance_km REAL DEFAULT 0,
            calories REAL DEFAULT 0,
            running_time_seconds INTEGER DEFAULT 0,
            water_liters REAL DEFAULT 0,
            UNIQUE(user_id, activity_date),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        );
        """
    )
    conn.commit()
    conn.close()


# Ensure database tables are created automatically on startup (e.g. under Gunicorn / Render)
init_db()


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def get_current_user():
    if "user_id" not in session:
        return None
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()


@app.context_processor
def inject_user():
    return {"current_user": get_current_user()}


def today_str():
    return date.today().isoformat()


def get_or_create_today_activity(user_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM daily_activity WHERE user_id = ? AND activity_date = ?",
        (user_id, today_str()),
    ).fetchone()
    if row is None:
        db.execute(
            "INSERT INTO daily_activity (user_id, activity_date) VALUES (?, ?)",
            (user_id, today_str()),
        )
        db.commit()
        row = db.execute(
            "SELECT * FROM daily_activity WHERE user_id = ? AND activity_date = ?",
            (user_id, today_str()),
        ).fetchone()
    return row


# ---------------------------------------------------------------------------
# Public pages
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Please fill in all fields.", "danger")
        else:
            flash("Thanks for reaching out! We'll get back to you soon.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not name or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        db = get_db()
        existing = db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("An account with that email already exists.", "danger")
            return render_template("register.html")

        db.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, generate_password_hash(password)),
        )
        db.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password"], password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        flash(f"Welcome back, {user['name']}!", "success")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    user = get_current_user()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        age = request.form.get("age") or None
        weight = request.form.get("weight") or None
        height = request.form.get("height") or None
        step_goal = request.form.get("daily_step_goal") or 10000
        water_goal = request.form.get("daily_water_goal") or 2.5

        db.execute(
            """UPDATE users SET name = ?, age = ?, weight = ?, height = ?,
               daily_step_goal = ?, daily_water_goal = ? WHERE id = ?""",
            (name, age, weight, height, step_goal, water_goal, user["id"]),
        )
        db.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", user=user)


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    today_activity = get_or_create_today_activity(user["id"])

    db = get_db()
    recent_runs = db.execute(
        "SELECT * FROM running_history WHERE user_id = ? ORDER BY created_at DESC LIMIT 5",
        (user["id"],),
    ).fetchall()

    step_goal = user["daily_step_goal"] or 10000
    water_goal = user["daily_water_goal"] or 2.5

    step_progress = min(100, round((today_activity["steps"] or 0) / step_goal * 100)) if step_goal else 0
    water_progress = min(100, round((today_activity["water_liters"] or 0) / water_goal * 100)) if water_goal else 0

    return render_template(
        "dashboard.html",
        user=user,
        activity=today_activity,
        recent_runs=recent_runs,
        step_goal=step_goal,
        water_goal=water_goal,
        step_progress=step_progress,
        water_progress=water_progress,
    )


# ---------------------------------------------------------------------------
# Running tracker
# ---------------------------------------------------------------------------

@app.route("/running")
@login_required
def running():
    db = get_db()
    history = db.execute(
        "SELECT * FROM running_history WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],),
    ).fetchall()
    return render_template("running.html", history=history)


@app.route("/api/running/save", methods=["POST"])
@login_required
def save_run():
    data = request.get_json(force=True)
    user_id = session["user_id"]

    duration_seconds = int(data.get("duration_seconds", 0))
    distance_km = float(data.get("distance_km", 0))
    route = data.get("route", [])

    avg_speed = round((distance_km / (duration_seconds / 3600)), 2) if duration_seconds > 0 else 0

    user = get_current_user()
    weight = user["weight"] or 70
    hours = duration_seconds / 3600
    met = 9.8
    calories = round(met * weight * hours, 1)

    db = get_db()
    db.execute(
        """INSERT INTO running_history
           (user_id, run_date, start_time, end_time, duration_seconds, distance_km,
            avg_speed_kmh, calories, route_json)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            user_id,
            today_str(),
            data.get("start_time"),
            data.get("end_time"),
            duration_seconds,
            distance_km,
            avg_speed,
            calories,
            str(route),
        ),
    )

    activity = get_or_create_today_activity(user_id)
    new_distance = (activity["distance_km"] or 0) + distance_km
    new_calories = (activity["calories"] or 0) + calories
    new_time = (activity["running_time_seconds"] or 0) + duration_seconds
    estimated_steps = int(distance_km * 1300)
    new_steps = (activity["steps"] or 0) + estimated_steps

    db.execute(
        """UPDATE daily_activity SET distance_km = ?, calories = ?, running_time_seconds = ?,
           steps = ? WHERE user_id = ? AND activity_date = ?""",
        (new_distance, new_calories, new_time, new_steps, user_id, today_str()),
    )
    db.commit()

    return jsonify({
        "success": True,
        "distance_km": round(distance_km, 2),
        "duration_seconds": duration_seconds,
        "avg_speed_kmh": avg_speed,
        "calories": calories,
    })


# ---------------------------------------------------------------------------
# Calories calculator
# ---------------------------------------------------------------------------

@app.route("/calories", methods=["GET", "POST"])
@login_required
def calories():
    result = None
    if request.method == "POST":
        age = float(request.form.get("age", 0) or 0)
        weight = float(request.form.get("weight", 0) or 0)
        duration_min = float(request.form.get("duration", 0) or 0)
        distance = float(request.form.get("distance", 0) or 0)

        hours = duration_min / 60
        speed = (distance / hours) if hours > 0 else 0

        if speed < 8:
            met = 8.3
        elif speed < 11:
            met = 9.8
        elif speed < 13:
            met = 11.0
        else:
            met = 12.8

        age_factor = 1.0
        if age > 50:
            age_factor = 0.92
        elif age < 20:
            age_factor = 1.05

        result = round(met * weight * hours * age_factor, 1)

    return render_template("calories.html", result=result)


# ---------------------------------------------------------------------------
# Water tracker
# ---------------------------------------------------------------------------

@app.route("/water", methods=["GET", "POST"])
@login_required
def water():
    user_id = session["user_id"]
    db = get_db()

    if request.method == "POST":
        amount = float(request.form.get("amount", 0) or 0)
        if amount > 0:
            db.execute(
                "INSERT INTO water_intake (user_id, log_date, amount_liters) VALUES (?, ?, ?)",
                (user_id, today_str(), amount),
            )
            activity = get_or_create_today_activity(user_id)
            new_total = (activity["water_liters"] or 0) + amount
            db.execute(
                "UPDATE daily_activity SET water_liters = ? WHERE user_id = ? AND activity_date = ?",
                (new_total, user_id, today_str()),
            )
            db.commit()
            flash(f"Added {amount} L of water.", "success")
        return redirect(url_for("water"))

    user = get_current_user()
    activity = get_or_create_today_activity(user_id)
    logs = db.execute(
        "SELECT * FROM water_intake WHERE user_id = ? AND log_date = ? ORDER BY logged_at DESC",
        (user_id, today_str()),
    ).fetchall()

    water_goal = user["daily_water_goal"] or 2.5
    progress = min(100, round((activity["water_liters"] or 0) / water_goal * 100)) if water_goal else 0

    return render_template(
        "water.html", logs=logs, activity=activity, water_goal=water_goal, progress=progress
    )


# ---------------------------------------------------------------------------
# Activity history
# ---------------------------------------------------------------------------

@app.route("/history")
@login_required
def history():
    db = get_db()
    records = db.execute(
        "SELECT * FROM daily_activity WHERE user_id = ? ORDER BY activity_date DESC",
        (session["user_id"],),
    ).fetchall()
    return render_template("history.html", records=records)


# ---------------------------------------------------------------------------
# Chart data API
# ---------------------------------------------------------------------------

@app.route("/api/charts/weekly")
@login_required
def weekly_chart_data():
    db = get_db()
    rows = db.execute(
        """SELECT activity_date, steps, distance_km, calories FROM daily_activity
           WHERE user_id = ? ORDER BY activity_date DESC LIMIT 7""",
        (session["user_id"],),
    ).fetchall()

    rows = list(reversed(rows))
    return jsonify({
        "labels": [r["activity_date"] for r in rows],
        "steps": [r["steps"] or 0 for r in rows],
        "distance": [r["distance_km"] or 0 for r in rows],
        "calories": [r["calories"] or 0 for r in rows],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
