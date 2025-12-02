#  Smart Task Analyzer

A full‑stack web application that helps users **analyze and prioritize tasks** based on importance, estimated hours, due dates, and dependencies.  
Frontend is deployed on **Vercel**, and backend API is powered by **Django on Render**.


# Live Demo
- **Frontend (UI):** [Smart Task Analyzer](https://task-analyzer-teal.vercel.app/)  
- **Backend (API):** `https://smart-task-analyzer-c6pf.onrender.com/`  


# Features
- Add tasks with attributes: title, importance, estimated hours, due date, dependencies.
- Analyze tasks via Django backend API → returns a **score** for each task.
- Results displayed as interactive cards in the frontend.
- Responsive UI built with HTML, CSS, and JavaScript.
- RESTful API built with Django, tested with Postman/RapidAPI Client.
- Deployed for free using **Vercel (frontend)** and **Render (backend)**.


# Tech Stack
**Frontend**
- HTML, CSS, JavaScript
- Bootstrap (for styling and layout)
- Fetch API for backend communication

**Backend**
- Django (Python)
- Django REST Framework (optional for API structuring)
- SQLite (default database)
- Gunicorn (for production server)
- django‑cors‑headers (for CORS handling)

**Deployment**
- Vercel → static frontend hosting
- Render → Django backend hosting


# Installation (Run Locally)

# 1. Clone the repository
```bash
git clone https://github.com/your-username/smart-task-analyzer.git
cd smart-task-analyzer
