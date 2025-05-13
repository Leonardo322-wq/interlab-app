import sqlite3

# Conexión a la base de datos
conn = sqlite3.connect('C:/Users/1022966950/Documents/Etiquetas/INTERLAB/interlaboratorios.db')
cursor = conn.cursor()

# Obtener la estructura de la tabla
cursor.execute("PRAGMA table_info(interlaboratorios);")
columnas = cursor.fetchall()

# Mostrar las columnas
print("Columnas en la tabla 'interlaboratorios':")
for columna in columnas:
    print(f"Nombre: {columna[1]}, Tipo: {columna[2]}")

# Cerrar la conexión
conn.close()
