from flask import Flask, render_template, request
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
    name = request.form["name"]
    role = request.form["role"]
    weekday = request.form["weekday"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("REPLACE INTO availability (name, role, weekday, start_time, end_time) VALUES (?, ?, ?, ?, ?)",
              (name, role, weekday, start_time, end_time))
    conn.commit()
    conn.close()
    return render_template("index.html", message="Verfügbarkeit gespeichert!")

@app.route("/check", methods=["POST"])
def check():
    weekday = request.form["weekday"]
    start_time = request.form["start_time"]
    end_time = request.form["end_time"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""
        SELECT name, role, start_time, end_time
        FROM availability
        WHERE weekday = ?
          AND NOT (
              end_time <= ? OR start_time >= ?
          )
        ORDER BY start_time
    """, (weekday, start_time, end_time))
    overlaps = c.fetchall()
    conn.close()

    return render_template("overlap.html", overlaps=overlaps, weekday=weekday, start_time=start_time, end_time=end_time)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
