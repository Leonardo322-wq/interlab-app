from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import os
import requests
import cloudinary
import cloudinary.uploader
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv(dotenv_path='datos.env')


# Configuración de Flask
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'clave_por_defecto')

# Inicializar Supabase
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL y SUPABASE_KEY deben estar definidos")


# Configurar Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# URL del coordinador
url_coordinador = ""

@app.route('/')
def index():
    interlabs = supabase.table('interlaboratorios').select("*").execute().data
    celulares = supabase.table('celulares').select("*").execute().data

    resultado = supabase.table("imagenes_generadas").select("url").order("fecha", desc=True).limit(1).execute()
    imagen_ruta = resultado.data[0]['url'] if resultado.data else ''

    timestamp = datetime.now().timestamp()

    return render_template('index.html', interlabs=interlabs, celulares=celulares, imagen_ruta=imagen_ruta, timestamp=timestamp)

@app.route('/registrar', methods=['POST'])
def registrar():
    data = {
        "nombre": request.form['nombre'],
        "parametros": request.form['parametros'],
        "fecha_entrega": request.form['fecha_entrega'],
        "analistas": request.form['analistas'],
        "estado": request.form['estado']
    }

    if not data['nombre'] or not data['fecha_entrega']:
        flash("El nombre y la fecha de entrega son obligatorios.")
        return redirect(url_for('index'))

    supabase.table('interlaboratorios').insert(data).execute()
    flash("Interlaboratorio registrado correctamente.")
    return redirect(url_for('index'))

@app.route('/agregar_celular', methods=['POST'])
def agregar_celular():
    numero = request.form['numero']
    observaciones = request.form['observaciones']

    if not numero:
        flash("El número celular es obligatorio.")
        return redirect(url_for('index'))

    data = {"numero": numero, "observaciones": observaciones}
    supabase.table('celulares').insert(data).execute()
    flash("Número celular agregado correctamente.")
    return redirect(url_for('index'))

@app.route('/upload_image', methods=['POST'])
def upload_image():
    image = request.files.get('image')
    if image:
        try:
            upload_result = cloudinary.uploader.upload(image, public_id="macrobalance_image", overwrite=True)
            url = upload_result.get('secure_url')
            print(f"✅ Imagen subida a Cloudinary: {url}")
            return url, 200
        except Exception as e:
            print("❌ Error al subir la imagen a Cloudinary:", e)
            return '❌ Error al subir imagen', 500
    return '❌ No se recibió imagen', 400

@app.route('/eliminar_celular/<int:id>', methods=['GET'])
def eliminar_celular(id):
    supabase.table('celulares').delete().eq('id', id).execute()
    flash("Número de celular eliminado correctamente.")
    return redirect(url_for('index'))

@app.route('/cambiar_estado/<int:id>', methods=['POST'])
def cambiar_estado(id):
    nuevo_estado = request.form['estado']
    supabase.table('interlaboratorios').update({"estado": nuevo_estado}).eq('id', id).execute()
    flash("Estado actualizado correctamente.")
    return redirect(url_for('index'))

@app.route('/eliminar_interlaboratorio/<int:id>', methods=['GET'])
def eliminar_interlaboratorio(id):
    supabase.table('interlaboratorios').delete().eq('id', id).execute()
    flash("Interlaboratorio eliminado correctamente.")
    return redirect(url_for('index'))

@app.route('/filtrar', methods=['POST'])
def filtrar_interlaboratorios():
    nombre = request.form.get('nombre', '')
    estado = request.form.get('estado', '')
    parametro = request.form.get('parametro', '')

    query = supabase.table('interlaboratorios').select('*')
    if nombre:
        query = query.ilike('nombre', f'%{nombre}%')
    if estado:
        query = query.ilike('estado', f'%{estado}%')
    if parametro:
        query = query.ilike('parametros', f'%{parametro}%')

    interlabs = query.execute().data
    celulares = supabase.table('celulares').select('*').execute().data

    resultado = supabase.table("imagenes_generadas").select("url").order("fecha", desc=True).limit(1).execute()
    imagen_ruta = resultado.data[0]['url'] if resultado.data else ''

    timestamp = datetime.now().timestamp()

    return render_template('index.html', interlabs=interlabs, celulares=celulares, imagen_ruta=imagen_ruta, timestamp=timestamp)

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

@app.route('/actualizar_observacion/<int:id>', methods=['POST'])
def actualizar_observacion(id):
    observaciones = request.form.get('observaciones')
    if not observaciones:
        flash("Debe ingresar una observación.")
        return redirect(url_for('index'))

    supabase.table('celulares').update({'observaciones': observaciones}).eq('id', id).execute()
    flash("Observación actualizada correctamente.")
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
