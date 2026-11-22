# IS211 Assignment 13 — Flask Quiz Tracker

A Flask and SQLite application for a teacher to manage students, quizzes, and quiz scores. Implements Parts I–VII only; no optional features.

## Run

1. Install Python 3 and Flask: `python -m pip install -r requirements.txt`
2. Run the application: `python app.py`
3. Open `http://127.0.0.1:5000/login`
4. Log in using username `admin` and password `password`.

The included `hw13.db` has the required sample student, quiz, and result. The `schema.sql` file defines the tables. To rebuild the sample database, run `python init_db.py` (this resets all data).

## Routes

- `/login` — teacher login
- `/dashboard` — students and quizzes
- `/student/add` — add student
- `/quiz/add` — add quiz
- `/student/<id>` — view a student's quiz IDs and scores
- `/results/add` — record quiz result
- `/logout` — log out
