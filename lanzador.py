import psycopg2
import schedule
import time
import threading
from datetime import datetime
import ctypes  # ← para mostrar el cuadro de mensaje

# 🔐 Datos de conexión PostgreSQL
DB_HOST = "dpg-d0iecn3e5dus73dr5ms0-a.oregon-postgres.render.com"
DB_NAME = "interlabdb"
DB_USER = "interlabdb_user"
DB_PASSWORD = "oDScvev1KDoyCkJW2rYngFV1wfn5R0DX"  # ← Reemplaza si cambias la clave

# 📁 Crear o limpiar log
with open("debug_log.txt", "w", encoding="utf-8") as f:
    f.write(f"[{datetime.now()}] Script iniciado correctamente.\n")

def log_debug(mensaje):
    with open("debug_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {mensaje}\n")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def mostrar_mensaje(titulo, mensaje):
    ctypes.windll.user32.MessageBoxW(0, mensaje, titulo, 0x40 | 0x1000)  # MB_ICONINFORMATION | MB_SYSTEMMODAL

def verificar_interlaboratorios():
    try:
        log_debug("Iniciando verificación de interlaboratorios...")
        conn = get_connection()
        cursor = conn.cursor()
        hoy = datetime.now().strftime('%Y-%m-%d')

        cursor.execute("""
            SELECT nombre, fecha_entrega
            FROM interlaboratorios
            WHERE estado ILIKE 'sin reportar' AND fecha_entrega >= %s
        """, (hoy,))
        resultados = cursor.fetchall()
        conn.close()

        if resultados:
            mensaje = "Buen día.\n\nExisten los siguientes interlaboratorios pendientes por reportar:\n\n"
            for nombre, fecha in resultados:
                mensaje += f"- {nombre} (fecha límite: {fecha})\n"

            mensaje += "\nToda la información en:\nhttps://interlab-app.onrender.com/"

            mostrar_mensaje("🔔 Interlaboratorios pendientes", mensaje)
            log_debug("📢 Mensaje mostrado en cuadro de diálogo.")
        else:
            log_debug("No hay interlaboratorios pendientes.")
    except Exception as e:
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] Error: {e}\n")
        log_debug("❌ Error al consultar la base de datos. Ver error_log.txt")

# ⏰ Tarea cada minuto para pruebas
schedule.every(1).minutes.do(verificar_interlaboratorios)

def ejecutar_programacion():
    while True:
        schedule.run_pending()
        time.sleep(5)

threading.Thread(target=ejecutar_programacion, daemon=True).start()

while True:
    time.sleep(10)
