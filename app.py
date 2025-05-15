from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import time
import threading
from datetime import datetime
import schedule
import os
import requests

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'clave_por_defecto')

# Obtener credenciales de PostgreSQL desde variables de entorno
DB_HOST = os.environ.get('DB_HOST')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

url_coordinador = ""  # Se actualizará vía POST /actualizar_url_coordinador


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )


def inicializar_base_de_datos_postgres():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interlaboratorios (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                parametros TEXT,
                fecha_entrega TEXT,
                analistas TEXT,
                estado TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS celulares (
                id SERIAL PRIMARY KEY,
                numero TEXT NOT NULL,
                observaciones TEXT
            )
        ''')

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Tablas verificadas/creadas correctamente en PostgreSQL.")
    except Exception as e:
        print(f"❌ Error al crear/verificar tablas: {e}")


@app.route('/')
def index():
    conn = get_connection()
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

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO interlaboratorios (nombre, parametros, fecha_entrega, analistas, estado)
        VALUES (%s, %s, %s, %s, %s)
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

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO celulares (numero, observaciones)
        VALUES (%s, %s)
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


@app.route('/eliminar_celular/<int:id>', methods=['GET'])
def eliminar_celular(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM celulares WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash("Número de celular eliminado correctamente.")
    return redirect(url_for('index'))


@app.route('/cambiar_estado/<int:id>', methods=['POST'])
def cambiar_estado(id):
    nuevo_estado = request.form['estado']
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE interlaboratorios SET estado = %s WHERE id = %s", (nuevo_estado, id))
    conn.commit()
    conn.close()
    flash("Estado actualizado correctamente.")
    return redirect(url_for('index'))


@app.route('/eliminar_interlaboratorio/<int:id>', methods=['GET'])
def eliminar_interlaboratorio(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM interlaboratorios WHERE id = %s", (id,))
    conn.commit()
    conn.close()
    flash("Interlaboratorio eliminado correctamente.")
    return redirect(url_for('index'))


@app.route('/filtrar', methods=['GET', 'POST'])
def filtrar_interlaboratorios():
    nombre = request.form.get('nombre', '')
    estado = request.form.get('estado', '')
    parametro = request.form.get('parametro', '')

    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM interlaboratorios WHERE 1=1"
    params = []

    if nombre:
        query += " AND nombre LIKE %s"
        params.append(f"%{nombre}%")
    if estado:
        query += " AND estado LIKE %s"
        params.append(f"%{estado}%")
    if parametro:
        query += " AND parametros LIKE %s"
        params.append(f"%{parametro}%")

    cursor.execute(query, tuple(params))
    interlabs = cursor.fetchall()
    conn.close()

    imagen_ruta = url_for('static', filename='images/macrobalance_image.png')
    timestamp = datetime.now().timestamp()
    return render_template('index.html', interlabs=interlabs, imagen_ruta=imagen_ruta, timestamp=timestamp)


@app.route('/enviar_mensaje_whatsapp', methods=['POST'])
def enviar_mensaje_whatsapp():
    global url_coordinador
    if not url_coordinador:
        flash("❌ La URL del coordinador no está configurada.")
        return redirect(url_for('index'))

    try:
        print(f"Intentando enviar petición POST a coordinador en: {url_coordinador}")
        response = requests.post(url_coordinador, timeout=15)
        print(f"Código respuesta: {response.status_code} - Contenido: {response.text}")

        if response.status_code == 200:
            flash("✅ Instrucción enviada al coordinador.")
        else:
            flash(f"⚠️ Falló el envío al coordinador. Código: {response.status_code}")
    except Exception as e:
        flash(f"❌ Error al contactar al coordinador: {e}")

    return redirect(url_for('index'))


@app.route('/actualizar_url_coordinador', methods=['POST'])
def actualizar_url_coordinador():
    global url_coordinador
    url = request.json.get("url")
    if url:
        url_coordinador = url
        print(f"✅ URL del coordinador actualizada: {url}")
        return {"status": "ok"}, 200
    return {"error": "URL no proporcionada"}, 400


def ejecutar_tareas_programadas():
    while True:
        schedule.run_pending()
        time.sleep(60)


inicializar_base_de_datos_postgres()

if __name__ == '__main__':
    thread = threading.Thread(target=ejecutar_tareas_programadas)
    thread.daemon = True
    thread.start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
