import win32com.client
import pyautogui
import os
import time
from datetime import datetime
import pythoncom

def capturar_imagen_excel():
    try:
        pythoncom.CoInitialize()

        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = True

        ruta = r'C:/Users/1022966950/Documents/Etiquetas/INTERLAB/MACRO BALANCE DE CILINDROS ACTUALIZADO.xlsm'
        wb = excel.Workbooks.Open(ruta)
        ws = wb.Sheets('BALANCE')
        ws.Activate()

        excel.WindowState = -4137  # Maximizar
        time.sleep(5)

        os.makedirs('static/images', exist_ok=True)
        screenshot = pyautogui.screenshot()
        screenshot.save('static/images/macrobalance_image.png')
        print(f"✅ Captura tomada a las {datetime.now().strftime('%H:%M')}")

        wb.Close(SaveChanges=False)
        excel.Quit()

    except Exception as e:
        print(f"❌ Error al capturar imagen: {e}")

    finally:
        pythoncom.CoUninitialize()

if __name__ == '__main__':
    capturar_imagen_excel()
