import mysql.connector
import csv

# Configura los detalles de tu conexión a la base de datos
db_config = {
    "host": "localhost",
    "user": "DefiiTest",
    "password": "Taracena12!",
    "database": "proyecto_umes_2023"
}

# Conectarse a la base de datos MySQL
conn = mysql.connector.connect(**db_config)

# Crear un cursor
cursor = conn.cursor()

# Ejecutar una consulta SQL
query = "SELECT * FROM `lecturas`"
cursor.execute(query)

# Obtener todos los registros de la consulta
data = cursor.fetchall()

# Obtener los nombres de las columnas
column_names = [description[0] for description in cursor.description]

# Cerrar la conexión a la base de datos
conn.close()

# Crear un archivo CSV y escribir los datos
with open('datos_proyecto_UMES_2023.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    
    # Escribir los encabezados (nombres de las columnas)
    csv_writer.writerow(column_names)
    
    # Escribir los datos
    csv_writer.writerows(data)

print("Los datos se han exportado a datos.csv")
