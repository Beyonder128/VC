from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from firebase_db import register_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = login_user(username, password)
        if user:
            session["user_id"]  = user["id"]
            session["role"]     = user["role"]
            session["username"] = user["username"]
            flash(f"Welcome back, {username}! 👋", "success")
            return redirect(url_for("doctor_dash") if user["role"] == "doctor" else url_for("patient_dash"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")
        role     = request.form.get("role", "")
        name     = request.form.get("name", "").strip()

        if not all([username, password, confirm, role, name]):
            flash("All fields are required.", "danger")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("register.html")

        if role == "doctor":
            specialization = request.form.get("specialization", "").strip()
            if not specialization:
                flash("Specialization is required for doctors.", "danger")
                return render_template("register.html")
            extra = {"name": name, "specialization": specialization}

        elif role == "patient":
            age = request.form.get("age", "").strip()
            if not age or not age.isdigit() or not (1 <= int(age) <= 120):
                flash("Valid age (1–120) is required for patients.", "danger")
                return render_template("register.html")
            extra = {"name": name, "age": age}

        else:
            flash("Invalid role selected.", "danger")
            return render_template("register.html")

        user_id = register_user(username, password, role, extra)
        if user_id is None:
            flash("Username already taken. Please choose another.", "danger")
            return render_template("register.html")

        flash("Account created! Please log in. ✅", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
