from flask import Flask, jsonify
import subprocess
import threading
import datetime

app = Flask(__name__)

@app.route('/ejecutar_whatsapp', methods=['POST'])
def ejecutar_whatsapp():
    def run_script():
        print(f"[{datetime.datetime.now()}] ▶️ Ejecutando enviar_whatsapp.py ...")
        try:
            # Puedes agregar shell=True si tienes problemas en Windows
            subprocess.call(["python", "enviar_whatsapp.py"])
            print(f"[{datetime.datetime.now()}] ✅ Script ejecutado correctamente.")
        except Exception as e:
            print(f"[{datetime.datetime.now()}] ❌ Error al ejecutar script: {e}")

    threading.Thread(target=run_script).start()
    return jsonify({"status": "Script de WhatsApp ejecutado"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
