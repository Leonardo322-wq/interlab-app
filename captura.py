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
import psutil

def cerrar_excel_si_esta_abierto():
    for proc in psutil.process_iter():
        try:
            if proc.name().lower() == "excel.exe":
                print(f"Cerrando Excel (PID {proc.pid}) para evitar bloqueos...")
                proc.kill()
                time.sleep(2)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

def traer_ventana_al_frente(hwnd):
    try:
        ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
        ctypes.windll.user32.SetForegroundWindow(hwnd)
    except Exception as e:
        print(f"No se pudo traer al frente la ventana: {e}")

def esperar_hasta_las_5_am():
    print("Esperando a que sean las 5:00 a.m. para ejecutar la captura...")
    while True:
        ahora = datetime.now()
        if ahora.hour == 8 and ahora.minute == 3:
            print("Es hora. Iniciando captura.")
            break
        time.sleep(30)

def capturar_imagen_excel():
    archivo_local = r'C:\Users\1022966950\Documents\Etiquetas\INTERLAB\Cilindros\MACRO_BALANCE_DE_CILINDROS.xlsm'
    try:
        cerrar_excel_si_esta_abierto()
        time.sleep(5)
        pythoncom.CoInitialize()

        ruta_origen = r'\\10.7.19.2\Laboratorio\ANALISIS DE MUESTRAS\REGISTROS\REGISTROS LABORATORIO 2025\10.Varios\METALES\CILINDROS\MACRO BALANCE DE CILINDROS ACTUALIZADO.xlsm'
        os.makedirs(os.path.dirname(archivo_local), exist_ok=True)

        shutil.copy2(ruta_origen, archivo_local)
        print(f"Archivo copiado a: {archivo_local}")

        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = True

        wb = excel.Workbooks.Open(archivo_local)
        ws = wb.Sheets('BALANCE')
        ws.Activate()

        hwnd = win32gui.FindWindow(None, excel.Caption)
        if hwnd:
            traer_ventana_al_frente(hwnd)

        excel.WindowState = -4137  # Maximizar
        time.sleep(5)

        os.makedirs('static/images', exist_ok=True)
        screenshot_path = 'static/images/macrobalance_image.png'
        pyautogui.screenshot(screenshot_path)
        print(f"Captura tomada a las {datetime.now().strftime('%H:%M')}")

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

        print(f"Captura recortada guardada a las {datetime.now().strftime('%H:%M')}")

    except Exception as e:
        print(f"Error al capturar imagen: {str(e)}")

    finally:
        pythoncom.CoUninitialize()
        if os.path.exists(archivo_local):
            try:
                os.remove(archivo_local)
                print("Archivo local eliminado.")
            except Exception as ex:
                print(f"No se pudo eliminar el archivo local: {ex}")

def subir_imagen_a_render():
    url = "https://interlab-app.onrender.com/upload_image"
    try:
        with open("static/images/macrobalance_image.png", "rb") as img:
            files = {"image": img}
            response = requests.post(url, files=files)
            print("Respuesta del servidor:", response.text)
    except FileNotFoundError:
        print("No se encontró la imagen para subir.")
    except Exception as e:
        print("Error al subir imagen:", e)

if __name__ == '__main__':
    esperar_hasta_las_5_am()
    capturar_imagen_excel()
    subir_imagen_a_render()
