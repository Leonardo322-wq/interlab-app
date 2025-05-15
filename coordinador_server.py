from flask import Flask
import subprocess
import threading

app = Flask(__name__)

@app.route('/ejecutar_whatsapp', methods=['POST'])
def ejecutar_whatsapp():
    def run_script():
        subprocess.call(["python", "enviar_whatsapp.py"])

    threading.Thread(target=run_script).start()
    return "✅ Script de WhatsApp ejecutado."

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
