from flask import Flask, render_template, request, redirect, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS availability (
                    name TEXT,
                    role TEXT,
                    weekday TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    UNIQUE(name, weekday)
                )''')
    conn.commit()
    conn.close()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    role = request.form.get("role", "").strip()
    weekday = request.form.get("weekday", "").strip()
    start_time = request.form.get("start_time", "").strip()
    end_time = request.form.get("end_time", "").strip()

    if not all([name, role, weekday, start_time, end_time]):
        return "Fehlende Eingabedaten", 400

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("REPLACE INTO availability (name, role, weekday, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
              (name, role, weekday, start_time, end_time))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/availability", methods=["GET"])
def availability():
    weekday = request.args.get("weekday")
    start = request.args.get("start")
    end = request.args.get("end")

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT name, role, start_time, end_time FROM availability WHERE weekday = ?", (weekday,))
    entries = c.fetchall()
    conn.close()

    overlapping = []
    for name, role, s, e in entries:
        if s <= end and e >= start:
            overlapping.append({"name": name, "role": role, "start": s, "end": e})

    return jsonify(overlapping)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)