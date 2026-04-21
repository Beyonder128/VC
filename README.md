# 🏥 DOCTOR Appointment Dashboard System

A **Flask-based Hospital Appointment Allotment System** designed to manage doctors, patients, and appointment scheduling efficiently through a clean web dashboard.

This project focuses on **real-world scheduling logic**, ensuring that appointment conflicts are avoided while maintaining a simple and scalable architecture.

---

## 🎯 Project Overview

This system allows hospitals or clinics to:

* Manage doctor records and specializations
* Register and manage patients
* Book appointments through a centralized dashboard
* Prevent double-booking of doctors
* View all scheduled appointments in a structured format

The application is built using **Flask, SQLite, Bootstrap 5, and Jinja2**, following a modular and maintainable design.

---

## 🚀 Key Features

### ✅ Core Functionalities

* 👨‍⚕️ Add and manage doctors
* 🧑‍🤝‍🧑 Add and manage patients
* 📅 Book appointments via dashboard
* ❌ Prevent overlapping appointments for the same doctor
* 📋 View all appointments in a tabular dashboard

---

### 🔥 Advanced Features (Planned / Extendable)

* Smart slot availability display
* Doctor filtering by specialization
* Appointment cancellation & rescheduling
* Waiting list / queue system
* Role-based authentication (Admin login)

---

## 🏗️ Project Structure

```bash
hospital_app/
│
├── app.py                 # Main Flask app
├── models.py              # Database connection & queries
├── database.db            # SQLite database
│
├── routes/                # Blueprint modules
│   ├── doctor_routes.py
│   ├── patient_routes.py
│   └── appointment_routes.py
│
├── templates/             # Jinja2 templates
│   ├── base.html
│   ├── dashboard.html
│   ├── doctors.html
│   ├── patients.html
│   ├── book.html
│
├── static/
│   └── styles.css         # Custom styling
```

---

## 🧠 Tech Stack

| Layer      | Technology        |
| ---------- | ----------------- |
| Backend    | Flask (Python)    |
| Database   | SQLite            |
| Frontend   | HTML, Bootstrap 5 |
| Templating | Jinja2            |

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Beyonder128/VC.git
cd VC
git checkout DOC-Appointment-Dashboard
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install flask
```

---

### 4️⃣ Run the Application

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:5000/
```

---

## 🧠 Database Schema

### 🩺 Doctors

* id (Primary Key)
* name
* specialization

### 🧑 Patients

* id (Primary Key)
* name
* age

### 📅 Appointments

* id (Primary Key)
* doctor_id (Foreign Key)
* patient_id (Foreign Key)
* time_slot

---

## ⚠️ Core Business Rule

> A doctor cannot have more than one appointment at the same time slot.

### ✔ Validation Logic:

* Before booking, system checks:

  * `doctor_id + time_slot`
* If exists → ❌ Reject booking
* Else → ✅ Confirm appointment

---

## 💻 Core Workflow

1. User selects doctor, patient, and time slot
2. System checks for conflicts in database
3. If slot is available → appointment is stored
4. If slot is taken → user is notified

---

## 🌐 UI Overview

The interface is built with **Bootstrap 5**, ensuring:

* Responsive layout
* Clean dashboard design
* Card-based forms
* Table-based data display

### Pages:

* **Dashboard** → Overview & navigation
* **Doctors Page** → Add/view doctors
* **Patients Page** → Add/view patients
* **Booking Page** → Schedule appointments

---

## 🧱 Development Approach

This project follows a structured build process:

1. Flask app & database setup
2. Doctor & patient modules
3. Appointment booking logic
4. UI implementation
5. Feature enhancements

---

## ⚠️ Common Issues

* Forgetting to check slot conflicts
* Mixing business logic with UI
* Hardcoding instead of using database
* Not using modular routes

---

## 📈 Future Improvements

* 🔐 Authentication system
* 📊 Analytics dashboard
* 🌐 REST API version
* ☁️ Cloud deployment
* 🧠 AI-based scheduling optimization

---

## 🤝 Contribution

Feel free to fork this repository and contribute improvements.

---

## 📌 Conclusion

This project demonstrates:

* Backend logic design
* Conflict handling in scheduling
* Modular Flask architecture
* Real-world system thinking

A strong addition to any **developer portfolio** when fully implemented.

---
