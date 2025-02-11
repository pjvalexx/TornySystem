from datetime import datetime, timedelta
from conexion.conexionBD import connectionBD

def obtener_ordenes_proximas():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                fecha_actual = datetime.now().date()
                fecha_limite = fecha_actual + timedelta(days=3)
                querySQL = """
                    SELECT wo.id, wo.description, wo.delivery_date, c.name AS client_name
                    FROM work_orders wo
                    JOIN clients c ON wo.client_id = c.id
                    WHERE wo.delivery_date BETWEEN %s AND %s
                    AND wo.status IN ('Pendiente', 'En Proceso')
                """
                cursor.execute(querySQL, (fecha_actual, fecha_limite))
                ordenes = cursor.fetchall()
        return ordenes
    except Exception as e:
        print(f"Error en obtener_ordenes_proximas: {e}")
        return []
    
def generar_alertas():
    ordenes_proximas = obtener_ordenes_proximas()
    alertas = []
    for orden in ordenes_proximas:
        alerta = f"La orden de trabajo '{orden['description']}' para el cliente '{orden['client_name']}' tiene una fecha de entrega próxima: {orden['delivery_date']}"
        alertas.append(alerta)
    return alertas

def obtener_alertas_stock():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT name, quantity, minimum_stock
                    FROM materials
                    WHERE quantity <= minimum_stock
                """
                cursor.execute(querySQL)
                alertas_stock = cursor.fetchall()
        return alertas_stock
    except Exception as e:
        print(f"Error en obtener_alertas_stock: {e}")
        return []

def generar_alertas_stock():
    alertas_stock = obtener_alertas_stock()
    alertas = []
    for alerta in alertas_stock:
        mensaje = f"El material '{alerta['name']}' ha llegado a su stock mínimo: {alerta['quantity']} unidades (mínimo: {alerta['minimum_stock']} unidades)"
        alertas.append(mensaje)
    return alertas