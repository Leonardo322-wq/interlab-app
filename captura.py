import win32com.client
import pyautogui
import os
import time
import shutil
from datetime import datetime
from PIL import Image
import pythoncom
import requests
import ctypes
import win32gui
import tempfile

def traer_ventana_al_frente(hwnd):
    try:
        ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"❌ No se pudo traer al frente la ventana: {e}")

def capturar_imagen_excel():
    try:
        pythoncom.CoInitialize()

        # Ruta original en red
        ruta_origen = r'Y:\ANALISIS DE MUESTRAS\REGISTROS\REGISTROS LABORATORIO 2025\10.Varios\METALES\CILINDROS\MACRO BALANCE DE CILINDROS ACTUALIZADO.xlsm'

        # Crear archivo temporal en el sistema
        temp_dir = tempfile.gettempdir()
        archivo_temp = os.path.join(temp_dir, 'MACRO_TEMP.xlsm')

        # Copiar el archivo de red a temporal local
        shutil.copy2(ruta_origen, archivo_temp)
        print(f"✅ Archivo copiado temporalmente a: {archivo_temp}")

        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = True

        wb = excel.Workbooks.Open(archivo_temp)
        ws = wb.Sheets('BALANCE')
        ws.Activate()

        hwnd = win32gui.FindWindow(None, excel.Caption)
        if hwnd:
            traer_ventana_al_frente(hwnd)

        excel.WindowState = -4137  # Maximizar
        time.sleep(5)

        os.makedirs('static/images', exist_ok=True)
        screenshot = pyautogui.screenshot()
        screenshot_path = 'static/images/macrobalance_image.png'
        screenshot.save(screenshot_path)
        print(f"✅ Captura tomada a las {datetime.now().strftime('%H:%M')}")

        wb.Close(SaveChanges=False)
        excel.Quit()

        imagen = Image.open(screenshot_path)
        width, height = imagen.size

        left = 26
        top = 216
        right = width - 26
        bottom = height - 99

        imagen_recortada = imagen.crop((left, top, right, bottom))
        imagen_recortada.save(screenshot_path)

        print(f"✅ Captura recortada guardada a las {datetime.now().strftime('%H:%M')}")

    except Exception as e:
        print(f"❌ Error al capturar imagen: {e}")

    finally:
        pythoncom.CoUninitialize()

def subir_imagen_a_render():
    url = "https://interlab-app.onrender.com/upload_image"
    with open("static/images/macrobalance_image.png", "rb") as img:
        files = {"image": img}
        try:
            response = requests.post(url, files=files)
            print(response.text)
        except Exception as e:
            print("Error al subir imagen:", e)

if __name__ == '__main__':
    capturar_imagen_excel()
    subir_imagen_a_render()
