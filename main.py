from __future__ import annotations

import random, threading
from flask import Flask, render_template, abort, jsonify

from services.student_data import fetch_students, GROUPS  # NEW unified data layer
from quotes import MESSAGES

app = Flask(__name__, static_folder="static", static_url_path="/static")
app.secret_key = "your_secret_key_here"

@app.route("/<group_name>")
def wheel_of_fortune(group_name: str):
    if group_name not in GROUPS:
        abort(404)

    students = fetch_students(group_name)
    if not students:
        return "Нет данных о студентах", 500

    # Format for JS front‑end (keep only the data it actually needs)
    formatted = [{"name": s["name"], "score": round(s["score"], 2)} for s in students]
    return render_template("wheel.html", students=formatted)

@app.route("/")
def main_page():
    return render_template("main.html")


last_index = {"value": -1}
lock = threading.Lock()

@app.route("/next-message")
def next_message():
    with lock:
        available = list(range(len(MESSAGES)))
        if last_index["value"] in available:
            available.remove(last_index["value"])

        if not available:
            available = list(range(len(MESSAGES)))

        idx = random.choice(available)
        last_index["value"] = idx

    return jsonify({"message": MESSAGES[idx]})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
