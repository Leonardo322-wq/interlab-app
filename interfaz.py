import sqlite3
import os
import tkinter as tk
from tkinter import ttk, messagebox

# Ruta de la base de datos en la carpeta compartida
db_path = r"C:\Users\1022966950\Documents\Etiquetas\INTERLAB\interlaboratorios.db"

# Crear conexión
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Crear las tablas si no existen
def crear_tablas():
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interlaboratorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        parametros TEXT,
        fecha_entrega DATE,
        analistas TEXT,
        estado TEXT,
        imagen BLOB,
        timestamp_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS celulares (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero TEXT,
        observaciones TEXT
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS log_envios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        interlaboratorio_id INTEGER,
        enviado_por_equipo TEXT,
        FOREIGN KEY (interlaboratorio_id) REFERENCES interlaboratorios(id)
    );
    ''')

    conn.commit()

# Insertar nuevo interlaboratorio
def insertar_interlaboratorio(nombre, parametros, fecha_entrega, analistas, estado, imagen=None):
    cursor.execute('''
    INSERT INTO interlaboratorios (nombre, parametros, fecha_entrega, analistas, estado, imagen)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (nombre, parametros, fecha_entrega, analistas, estado, imagen))
    conn.commit()

# Insertar número de celular
def insertar_celular(numero, observaciones):
    cursor.execute('''
    INSERT INTO celulares (numero, observaciones)
    VALUES (?, ?)
    ''', (numero, observaciones))
    conn.commit()

# Crear interfaz gráfica
def crear_interfaz():
    ventana = tk.Tk()
    ventana.title("Gestión de Interlaboratorios")
    ventana.geometry("600x400")

    # Formulario de registro
    tk.Label(ventana, text="Nombre del Interlaboratorio").grid(row=0, column=0, padx=10, pady=10)
    nombre_entry = tk.Entry(ventana)
    nombre_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(ventana, text="Parámetros").grid(row=1, column=0, padx=10, pady=10)
    parametros_entry = tk.Entry(ventana)
    parametros_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(ventana, text="Fecha de Entrega (AAAA-MM-DD)").grid(row=2, column=0, padx=10, pady=10)
    fecha_entrega_entry = tk.Entry(ventana)
    fecha_entrega_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(ventana, text="Analistas").grid(row=3, column=0, padx=10, pady=10)
    analistas_entry = tk.Entry(ventana)
    analistas_entry.grid(row=3, column=1, padx=10, pady=10)

    tk.Label(ventana, text="Estado").grid(row=4, column=0, padx=10, pady=10)
    estado_combobox = ttk.Combobox(ventana, values=["Reportado", "Sin reportar"])
    estado_combobox.grid(row=4, column=1, padx=10, pady=10)

    # Botón para guardar
    def guardar():
        nombre = nombre_entry.get()
        parametros = parametros_entry.get()
        fecha_entrega = fecha_entrega_entry.get()
        analistas = analistas_entry.get()
        estado = estado_combobox.get()

        if nombre and parametros and fecha_entrega and analistas and estado:
            insertar_interlaboratorio(nombre, parametros, fecha_entrega, analistas, estado)
            messagebox.showinfo("Éxito", "Interlaboratorio registrado correctamente.")
            # Limpiar campos
            nombre_entry.delete(0, tk.END)
            parametros_entry.delete(0, tk.END)
            fecha_entrega_entry.delete(0, tk.END)
            analistas_entry.delete(0, tk.END)
            estado_combobox.set('')
        else:
            messagebox.showerror("Error", "Por favor complete todos los campos.")

    tk.Button(ventana, text="Guardar", command=guardar).grid(row=5, column=0, columnspan=2, pady=20)

    ventana.mainloop()

# Ejecutar
if __name__ == "__main__":
    crear_tablas()
    crear_interfaz()
