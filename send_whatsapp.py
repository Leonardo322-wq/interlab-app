import time
import schedule
from datetime import datetime, timedelta
import psycopg2
import pywhatkit
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Función para conectarse a PostgreSQL
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
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
    print("Ejecutando tarea programada...")
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

        for interlab in interlabs:
            nombre = interlab[0]
            fecha_entrega = datetime.strptime(interlab[1], "%Y-%m-%d").date()

            if fecha_entrega > fecha_actual:
                mensaje_completo += f"🔸 {nombre}, fecha de entrega: {fecha_entrega.strftime('%d/%m/%Y')}\n"

        # Enviar el mensaje si hay interlaboratorios pendientes
        if mensaje_completo != "📢 *Recordatorio de interlaboratorios pendientes:*\n\n":
            for celular in celulares:
                numero_celular = celular[0]
                if numero_celular:
                    enviar_por_whatsapp(numero_celular, mensaje_completo)
                    mensajes_enviados += 1

        if mensajes_enviados == 0:
            print("No hay interlaboratorios pendientes o no se han encontrado números válidos.")

        conn.close()
    except Exception as e:
        print("❌ Error durante la consulta o conexión a la base de datos:", e)

    print("✅ Tarea programada completada.")

# Cálculo de próxima ejecución (ajustada a las 16:22)
def calcular_proxima_ejecucion():
    now = datetime.now()
    next_run_time = now.replace(hour=16, minute=22, second=0, microsecond=0)
    if now > next_run_time:
        next_run_time += timedelta(days=1)
    return next_run_time

# Mostrar tiempo restante
def tiempo_restante():
    now = datetime.now()
    next_run_time = calcular_proxima_ejecucion()
    remaining = next_run_time - now
    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds // 60) % 60
    return f"⏳ Faltan {days} días, {hours} horas y {minutes} minutos para el próximo envío."

# Programar ejecución
def programar_tarea():
    schedule.every().day.at("16:22").do(enviar_notificacion)
    schedule.every(2).days.at("16:22").do(enviar_notificacion)
    print("🕒 Tarea programada para ejecutarse a las 16:22.")

def ejecutar_tareas_programadas():
    while True:
        schedule.run_pending()
        print(tiempo_restante())
        time.sleep(60)

if __name__ == '__main__':
    print("🚀 Iniciando script...")
    programar_tarea()
    ejecutar_tareas_programadas()
