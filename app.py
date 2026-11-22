import os
import sqlite3
from functools import wraps
from flask import Flask, flash, g, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'development-secret-change-me')
DATABASE = os.path.join(os.path.dirname(__file__), 'hw13.db')


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    return wrapped


@app.route('/')
def index():
    return redirect(url_for('dashboard') if session.get('logged_in') else url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('username') == 'admin' and request.form.get('password') == 'password':
            session.clear()
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        flash('Incorrect username or password.')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    students = db.execute('SELECT * FROM students ORDER BY id').fetchall()
    quizzes = db.execute('SELECT * FROM quizzes ORDER BY id').fetchall()
    return render_template('dashboard.html', students=students, quizzes=quizzes)


@app.route('/student/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        first = request.form.get('first_name', '').strip()
        last = request.form.get('last_name', '').strip()
        if not first or not last:
            flash('Both first and last name are required.')
        else:
            try:
                db = get_db()
                db.execute('INSERT INTO students (first_name, last_name) VALUES (?, ?)', (first, last))
                db.commit()
                return redirect(url_for('dashboard'))
            except sqlite3.Error:
                flash('Could not add student.')
    return render_template('add_student.html')


@app.route('/quiz/add', methods=['GET', 'POST'])
@login_required
def add_quiz():
    if request.method == 'POST':
        subject = request.form.get('subject', '').strip()
        date = request.form.get('quiz_date', '').strip()
        try:
            questions = int(request.form.get('questions', ''))
            if not subject or not date or questions <= 0:
                raise ValueError
            db = get_db()
            db.execute('INSERT INTO quizzes (subject, questions, quiz_date) VALUES (?, ?, ?)',
                       (subject, questions, date))
            db.commit()
            return redirect(url_for('dashboard'))
        except (ValueError, sqlite3.Error):
            flash('Enter a subject, a positive number of questions, and a date.')
    return render_template('add_quiz.html')


@app.route('/student/<int:id>')
@login_required
def student_results(id):
    db = get_db()
    student = db.execute('SELECT * FROM students WHERE id = ?', (id,)).fetchone()
    if student is None:
        return 'Student not found', 404
    results = db.execute('SELECT quiz_id, score FROM results WHERE student_id = ? ORDER BY quiz_id',
                         (id,)).fetchall()
    return render_template('student_results.html', student=student, results=results)


@app.route('/results/add', methods=['GET', 'POST'])
@login_required
def add_result():
    db = get_db()
    if request.method == 'POST':
        try:
            student_id = int(request.form.get('student_id', ''))
            quiz_id = int(request.form.get('quiz_id', ''))
            score = int(request.form.get('score', ''))
            if not 0 <= score <= 100:
                raise ValueError
            db.execute('INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)',
                       (student_id, quiz_id, score))
            db.commit()
            return redirect(url_for('dashboard'))
        except (ValueError, sqlite3.IntegrityError):
            db.rollback()
            flash('Choose a valid student and quiz, and enter a score from 0 to 100. A result may already exist.')
        except sqlite3.Error:
            db.rollback()
            flash('Could not save quiz result.')
    students = db.execute('SELECT * FROM students ORDER BY last_name, first_name').fetchall()
    quizzes = db.execute('SELECT * FROM quizzes ORDER BY id').fetchall()
    return render_template('add_result.html', students=students, quizzes=quizzes)


if __name__ == '__main__':
    app.run(debug=True)
