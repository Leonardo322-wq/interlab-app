
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import time
import threading
from datetime import datetime
import schedule
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

db_path = os.path.join(os.path.dirname(__file__), 'interlaboratorios.db')

def inicializar_base_de_datos():
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

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

@app.route('/registrar', methods=['POST'])
def registrar():
    nombre = request.form['nombre']
    parametros = request.form['parametros']
    fecha_entrega = request.form['fecha_entrega']
    analistas = request.form['analistas']
    estado = request.form['estado']
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

@app.route('/agregar_celular', methods=['POST'])
def agregar_celular():
    numero = request.form['numero']
    observaciones = request.form['observaciones']
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

@app.route('/upload_image', methods=['POST'])
def upload_image():
    image = request.files.get('image')
    if image:
        ruta_destino = os.path.join('static', 'images', 'macrobalance_image.png')
        image.save(ruta_destino)
        print(f"Imagen guardada en: {ruta_destino}")
        return '✅ Imagen subida correctamente', 200
    return '❌ No se recibió imagen', 400

def ejecutar_tareas_programadas():
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == '__main__':
    inicializar_base_de_datos()
    thread = threading.Thread(target=ejecutar_tareas_programadas)
    thread.daemon = True
    thread.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
