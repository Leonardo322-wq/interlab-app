import win32com.client as win32
import win32gui
import win32con
import os
import requests
import time
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from pathlib import Path
from supabase import create_client, Client


dotenv_path = Path(__file__).resolve().parent / 'datos.env'
print("ruta:", dotenv_path)
load_dotenv(dotenv_path=dotenv_path)

print("🌍 Cloud name:", os.environ.get('CLOUDINARY_CLOUD_NAME'))
print("🔑 API key:", os.environ.get('CLOUDINARY_API_KEY'))
print("🕵️‍♂️ API secret:", os.environ.get('CLOUDINARY_API_SECRET'))

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def subir_imagen_a_cloudinary():
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )

    try:
        result = cloudinary.uploader.upload(
            "static/images/macrobalance_image.png",
            public_id="macrobalance_image",
            overwrite=True,
            invalidate=True,
            resource_type="image"
        )
        url = result['secure_url']
        print("✅ Imagen subida a Cloudinary:", url)

        # Guardar URL en Supabase
        supabase.table("imagenes_generadas").insert({"url": url}).execute()
        print("✅ URL guardada en Supabase.")

    except Exception as e:
        print("❌ Error al subir a Cloudinary o guardar URL:", e)


def exportar_imagen(max_reintentos=3):
    archivo_excel = r'\\10.7.19.2\Laboratorio\ANALISIS DE MUESTRAS\REGISTROS\REGISTROS LABORATORIO 2025\10.Varios\METALES\CILINDROS\MACRO BALANCE DE CILINDROS ACTUALIZADO.xlsm'

    if not os.path.exists(archivo_excel):
        print(f"❌ El archivo no existe: {archivo_excel}")
        return

    intentos = 0
    while intentos < max_reintentos:
        try:
            print(f"🔄 Intento {intentos + 1} de {max_reintentos}...")
            excel = win32.gencache.EnsureDispatch("Excel.Application")
            excel.Visible = True

            libro = excel.Workbooks.Open(archivo_excel)

            # Traer ventana al frente
            hwnd = win32gui.FindWindow(None, excel.Caption)
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)

            # Limpiar celda de control antes de correr macro
            hoja_control = libro.Sheets("BALANCE")
            hoja_control.Range("A53").Value = ""

            # Ejecutar macro
            excel.Application.Run("ExportarRangoComoImagen_UsandoPowerPoint")

            # Esperar unos segundos a que termine
            time.sleep(3)

            # Leer resultado
            resultado = hoja_control.Range("A53").Value

            if resultado == "OK":
                print("✅ Macro ejecutada correctamente.")
                libro.Close(SaveChanges=False)
                excel.Quit()
                subir_imagen_a_cloudinary()
                break
            else:
                print("⚠️ La macro reportó un error. Reintentando...")
                libro.Close(SaveChanges=False)
                excel.Quit()
                intentos += 1
                time.sleep(2)
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            intentos += 1
            time.sleep(2)

    if intentos == max_reintentos:
        print("❌ Se alcanzó el número máximo de intentos. Revisa la macro.")

if __name__ == "__main__":
    exportar_imagen()
