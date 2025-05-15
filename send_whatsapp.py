import time
import schedule
from datetime import datetime
import psycopg2
import pywhatkit

# 🔐 Datos de conexión PostgreSQL
DB_HOST = "dpg-d0iecn3e5dus73dr5ms0-a.oregon-postgres.render.com"
DB_NAME = "interlabdb"
DB_USER = "interlabdb_user"
DB_PASSWORD = "oDScvev1KDoyCkJW2rYngFV1wfn5R0DX"  # Reemplaza si cambias la clave

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

# Enviar mensaje por WhatsApp a un número específico
def enviar_por_whatsapp(numero, mensaje):
    try:
        print(f"Enviando mensaje a {numero}...")
        pywhatkit.sendwhatmsg_instantly(
            phone_no=numero,
            message=mensaje,
            wait_time=10,
            tab_close=True,
            close_time=3
        )
        print(f"Mensaje enviado a {numero}.")
    except Exception as e:
        print(f"Error al enviar mensaje a {numero}:", e)

# Función principal que consulta la base de datos y envía mensajes
def enviar_notificacion():
    print(f"Ejecutando tarea programada a las {datetime.now().strftime('%H:%M:%S')}...")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Consultar los interlaboratorios pendientes
        cursor.execute("SELECT nombre, fecha_entrega FROM interlaboratorios WHERE estado = 'Sin reportar'")
        interlabs = cursor.fetchall()

        # Consultar los números de celular
        cursor.execute("SELECT numero FROM celulares")
        celulares = cursor.fetchall()

        fecha_actual = datetime.now().date()
        mensajes_enviados = 0

        # Construir el mensaje con todos los interlaboratorios pendientes
        mensaje_completo = "📢 *Recordatorio de interlaboratorios pendientes:*\n\n"

        for nombre, fecha_str in interlabs:
            fecha_entrega = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            if fecha_entrega >= fecha_actual:
                mensaje_completo += f"🔸 {nombre}, fecha de entrega: {fecha_entrega.strftime('%d/%m/%Y')}\n"

        # Enviar el mensaje si hay interlaboratorios pendientes
        if mensaje_completo != "📢 *Recordatorio de interlaboratorios pendientes:*\n\n":
            for (numero_celular,) in celulares:
                if numero_celular:
                    enviar_por_whatsapp(numero_celular, mensaje_completo)
                    mensajes_enviados += 1
        else:
            print("No hay interlaboratorios pendientes para enviar.")

        if mensajes_enviados == 0 and mensaje_completo != "📢 *Recordatorio de interlaboratorios pendientes:*\n\n":
            print("No se encontraron números válidos para enviar mensajes.")

        cursor.close()
        conn.close()

    except Exception as e:
        print("❌ Error durante la consulta o conexión a la base de datos:", e)

    print("✅ Tarea programada completada.")

# Programar tarea para que se ejecute una vez al día a las 14:35
def programar_tarea():
    schedule.clear()
    schedule.every().day.at("14:42").do(enviar_notificacion)
    print("🕒 Tarea programada para ejecutarse a las 14:35.")

def ejecutar_tareas_programadas():
    while True:
        schedule.run_pending()
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Esperando próxima tarea...")
        time.sleep(10)

if __name__ == '__main__':
    print("🚀 Iniciando script...")
    programar_tarea()
    ejecutar_tareas_programadas()
