from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
import os

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except:
    psycopg2 = None

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")


# -------------------------
# CONEXIÓN A BASE DE DATOS
# -------------------------
def get_db_connection():
    if DATABASE_URL and psycopg2:
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)

        # CLAVE: sslmode=require para Render
        conn = psycopg2.connect(url, sslmode="require", cursor_factory=RealDictCursor)
        return conn
    else:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        return conn


# -------------------------
# CREAR TABLA
# -------------------------
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    if DATABASE_URL:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invitados (
            id SERIAL PRIMARY KEY,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            asistencia TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
        """)
    else:
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
        cursor = conn.cursor()

        if DATABASE_URL and psycopg2:
            cursor.execute(
                "INSERT INTO invitados (nombre, apellido, asistencia, fecha) VALUES (%s,%s,%s,%s)",
                 (nombre, apellido, asistencia, fecha)
            )
        else:
            cursor.execute(
                "INSERT INTO invitados (nombre, apellido, asistencia, fecha) VALUES (?,?,?,?)",
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
# ADMIN
# -------------------------
@app.route("/admin")
def admin():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM invitados ORDER BY id DESC")
    invitados = cursor.fetchall()

    conn.close()

    total = sum(1 for i in invitados if i["asistencia"] == "Si")

    return render_template("admin.html", invitados=invitados, total=total)


# -------------------------
# ELIMINAR
# -------------------------
@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if DATABASE_URL:
        cursor.execute("DELETE FROM invitados WHERE id=%s", (id,))
    else:
        cursor.execute("DELETE FROM invitados WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect(url_for("admin"))


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)