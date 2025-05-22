import time
from datetime import datetime
import psycopg2
import pywhatkit

# 🔐 Datos de conexión PostgreSQL
DB_HOST = "dpg-d0iecn3e5dus73dr5ms0-a.oregon-postgres.render.com"
DB_NAME = "interlabdb"
DB_USER = "interlabdb_user"
DB_PASSWORD = "oDScvev1KDoyCkJW2rYngFV1wfn5R0DX"

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

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
        print(f"✅ Mensaje enviado a {numero}.")
    except Exception as e:
        print(f"❌ Error al enviar mensaje a {numero}:", e)

def enviar_notificacion():
    print(f"🟡 Ejecutando envío manual a las {datetime.now().strftime('%H:%M:%S')}...")
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Interlabs sin reportar y aún vigentes
        cursor.execute("SELECT nombre, fecha_entrega FROM interlaboratorios WHERE estado = 'Sin reportar'")
        interlabs = cursor.fetchall()

        # Celulares a los que se enviará
        cursor.execute("SELECT numero FROM celulares")
        celulares = cursor.fetchall()

        fecha_actual = datetime.now().date()
        mensaje_completo = "📢 *Recordatorio de interlaboratorios pendientes:*\n\n"
        hay_pendientes = False

        for nombre, fecha_str in interlabs:
            fecha_entrega = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            if fecha_entrega >= fecha_actual:
                mensaje_completo += f"🔸 {nombre}, fecha de entrega: {fecha_entrega.strftime('%d/%m/%Y')}\n"
                hay_pendientes = True

        if hay_pendientes:
            mensaje_completo += "\n📎 Si deseas ver toda la información accede a: https://interlab-app.onrender.com"
            for (numero_celular,) in celulares:
                if numero_celular:
                    enviar_por_whatsapp(numero_celular, mensaje_completo)
        else:
            print("✅ No hay interlaboratorios pendientes por enviar.")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error al consultar la base de datos: {e}")

if __name__ == '__main__':
    enviar_notificacion()
