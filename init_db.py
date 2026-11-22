import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
with sqlite3.connect(ROOT / 'hw13.db') as db:
    db.execute('PRAGMA foreign_keys = ON')
    db.executescript((ROOT / 'schema.sql').read_text())
    db.execute('INSERT INTO students (first_name, last_name) VALUES (?, ?)', ('John', 'Smith'))
    db.execute('INSERT INTO quizzes (subject, questions, quiz_date) VALUES (?, ?, ?)',
               ('Python Basics', 5, '2015-02-05'))
    db.execute('INSERT INTO results (student_id, quiz_id, score) VALUES (?, ?, ?)', (1, 1, 85))
    db.commit()
print('Initialized hw13.db with sample data.')
