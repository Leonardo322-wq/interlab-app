import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import os
import sys
import time
from datetime import datetime

class CapturaService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CapturaExcelService"
    _svc_display_name_ = "Servicio de Captura de Imagen Excel a las 5am"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.script_path = os.path.join(os.path.dirname(__file__), "captura.py")
        self.last_execution_date = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("🟢 Servicio iniciado correctamente.")
        while True:
            now = datetime.now()
            if now.hour == 9 and now.minute == 3:
                today = now.date()
                if self.last_execution_date != today:
                    try:
                        servicemanager.LogInfoMsg("⚙️ Ejecutando captura.py")
                        subprocess.call([sys.executable, self.script_path])
                        self.last_execution_date = today
                    except Exception as e:
                        servicemanager.LogErrorMsg(f"❌ Error ejecutando captura.py: {e}")
                time.sleep(60)  # Espera 1 minuto antes de volver a comprobar
            else:
                time.sleep(30)  # Espera 30 segundos en horas no relevantes

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(CapturaService)
