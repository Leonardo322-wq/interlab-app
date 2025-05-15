import subprocess
import time
import requests
import json

def obtener_url_ngrok():
    try:
        resultado = subprocess.check_output("curl http://127.0.0.1:4040/api/tunnels", shell=True)
        data = json.loads(resultado)
        for tunel in data['tunnels']:
            if tunel['proto'] == 'https':
                return tunel['public_url']
    except Exception as e:
        print(f"❌ Error al obtener la URL de ngrok: {e}")
    return None

# Esperar a que ngrok genere su URL
print("⏳ Esperando que ngrok genere la URL...")
url_ngrok = None
for _ in range(10):
    url_ngrok = obtener_url_ngrok()
    if url_ngrok:
        break
    time.sleep(2)

if not url_ngrok:
    print("❌ No se pudo obtener la URL de ngrok.")
    exit()

print(f"✅ URL de ngrok obtenida: {url_ngrok}")

# Enviar la URL a tu app en Render
render_url = "https://interlab-app.onrender.com/actualizar_url_coordinador"
payload = {"url": f"{url_ngrok}/ejecutar_whatsapp"}

try:
    response = requests.post(render_url, json=payload, timeout=10)
    if response.status_code == 200:
        print("✅ URL enviada exitosamente a la web.")
    else:
        print(f"⚠️ Fallo al enviar la URL. Código: {response.status_code}")
except Exception as e:
    print(f"❌ Error al enviar URL a Render: {e}")
