import mysql.connector
#CONFIGURACION DE LA BASE DE DATOS
db_config = {
    'host': 'localhost',
    'user': 'genarodesarrollo',
    'password': 'password',
    'database': 'sistema-ventas'
}
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection