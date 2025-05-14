from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import time
import threading
from datetime import datetime
from twilio.rest import Client
from plyer import notification
import schedule
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db_path = os.path.join(os.path.dirname(__file__), 'interlaboratorios.db')


# Crear la base de datos y las tablas si no existen
def inicializar_base_de_datos():
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Crear tabla interlaboratorios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interlaboratorios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                parametros TEXT,
                fecha_entrega TEXT,
                analistas TEXT,
                estado TEXT
            )
        ''')

        # Crear tabla celulares
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS celulares (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL,
                observaciones TEXT
            )
        ''')

        conn.commit()
        conn.close()
        print("Base de datos y tablas creadas correctamente.")
    else:
        print("La base de datos ya existe.")

# Función para enviar un SMS a un número
def enviar_sms(numero, mensaje):
    message = client.messages.create(
        body=mensaje,
        from_=twilio_phone_number,
        to=numero
    )

# Función para enviar una notificación en el sistema operativo
def enviar_notificacion(titulo, mensaje):
    notification.notify(
        title=titulo,
        message=mensaje,
        timeout=10  # Duración de la notificación en segundos
    )

# Enviar notificación en la computadora a las 8:00 AM
def enviar_notificaciones():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT nombre, estado, fecha_entrega FROM interlaboratorios")
    interlabs = cursor.fetchall()

    fecha_actual = datetime.now().date()

    for interlab in interlabs:
        nombre = interlab[0]
        estado = interlab[1]
        fecha_entrega = datetime.strptime(interlab[2], "%Y-%m-%d").date()

        if estado == "Sin reportar" and fecha_entrega > fecha_actual:
            enviar_notificacion(
                f"Interlaboratorio pendiente: {nombre}",
                f"El interlaboratorio {nombre} está pendiente de reporte y tiene fecha de entrega {fecha_entrega.strftime('%d/%m/%Y')}."
            )

    conn.close()

schedule.every().day.at("08:00").do(enviar_notificaciones)

# Ejecutar las tareas programadas en segundo plano
def ejecutar_tareas_programadas():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Ruta principal
@app.route('/')
def index():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interlaboratorios")
    interlabs = cursor.fetchall()

    cursor.execute("SELECT * FROM celulares")
    celulares = cursor.fetchall()

    conn.close()

    imagen_ruta = url_for('static', filename='images/macrobalance_image.png')
    timestamp = datetime.now().timestamp()

    return render_template('index.html', interlabs=interlabs, celulares=celulares, imagen_ruta=imagen_ruta, timestamp=timestamp)

# Registrar interlaboratorio
@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form['nombre']
    parametros = request.form['parametros']
    fecha_entrega = request.form['fecha_entrega']
    analistas = request.form['analistas']
    estado = request.form['estado']

    # Validación simple
    if not nombre or not fecha_entrega:
        flash("El nombre y la fecha de entrega son obligatorios.")
        return redirect(url_for('index'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO interlaboratorios (nombre, parametros, fecha_entrega, analistas, estado)
        VALUES (?, ?, ?, ?, ?)
    ''', (nombre, parametros, fecha_entrega, analistas, estado))

    conn.commit()
    conn.close()

    flash("Interlaboratorio registrado correctamente.")
    return redirect(url_for('index'))

# Agregar número celular
@app.route('/agregar_celular', methods=['POST'])
def agregar_celular():
    numero = request.form['numero']
    observaciones = request.form['observaciones']

    # Validación simple
    if not numero:
        flash("El número celular es obligatorio.")
        return redirect(url_for('index'))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO celulares (numero, observaciones)
        VALUES (?, ?)
    ''', (numero, observaciones))

    conn.commit()
    conn.close()

    flash("Número celular agregado correctamente.")
    return redirect(url_for('index'))

# Ejecutar hilo y Flask
if __name__ == '__main__':
    inicializar_base_de_datos()  # Crear DB y tablas si no existen

    thread = threading.Thread(target=ejecutar_tareas_programadas)
    thread.daemon = True
    thread.start()

    app.run(debug=True)
