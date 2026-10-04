import os
import psycopg2
from flask import Flask, request, redirect, render_template_string

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )

def init_db():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("""CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT NOW())""")

PAGE = """
<h1>Mes notes (app cloud)</h1>
<form method="post" action="/add">
  <input name="content" placeholder="Ta note" required>
  <button>Ajouter</button>
</form>
<ul>{% for n in notes %}<li>{{ n[1] }} <small>({{ n[2] }})</small></li>{% endfor %}</ul>
"""

@app.route("/")
def index():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
        notes = cur.fetchall()
    return render_template_string(PAGE, notes=notes)

@app.route("/add", methods=["POST"])
def add():
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO notes (content) VALUES (%s)", (request.form["content"],))
    return redirect("/")

@app.route("/health")
def health():
    return "OK", 200

init_db()