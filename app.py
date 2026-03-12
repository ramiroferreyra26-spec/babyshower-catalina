from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os  

app = Flask(__name__)

DATABASE = os.environ.get("DATABASE_URL", "database.db")


# -------------------------
# CONEXIÓN A BASE DE DATOS
# -------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------
# CREAR TABLA SI NO EXISTE
# -------------------------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invitados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            asistencia TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


# 🔹 IMPORTANTE: asegurar que la DB exista siempre
init_db()


# -------------------------
# INDEX
# -------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        asistencia = request.form.get("asistencia")

        if not nombre or not apellido or not asistencia:
            return "Faltan datos"

        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO invitados (nombre, apellido, asistencia, fecha) VALUES (?, ?, ?, ?)",
            (nombre, apellido, asistencia, fecha)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("gracias"))

    return render_template("index.html")


# -------------------------
# GRACIAS
# -------------------------
@app.route("/gracias")
def gracias():
    return render_template("gracias.html")


# -------------------------
# PANEL ADMIN
# -------------------------
@app.route("/admin")
def admin():
    conn = get_db_connection()

    invitados = conn.execute(
        "SELECT * FROM invitados ORDER BY id DESC"
    ).fetchall()

    conn.close()

    total = sum(1 for i in invitados if i["asistencia"] == "Si")

    return render_template("admin.html", invitados=invitados, total=total)


# -------------------------
# ELIMINAR INVITADO (POST)
# -------------------------
@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM invitados WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# -------------------------
# INICIAR APP
# -------------------------
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)