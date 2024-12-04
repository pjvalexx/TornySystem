from conexion.conexionBD import connectionBD
from flask import session

def obtenerMateriales():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM materials"
                cursor.execute(querySQL)
                materiales = cursor.fetchall()
                return materiales
    except Exception as e:
        print(f"Error en obtenerMateriales: {e}")
        return []

from flask import session
from conexion.conexionBD import connectionBD

def procesar_form_material(dataForm):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    INSERT INTO materials (name, description, quantity, unit, minimum_stock, supplier_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                valores = (
                    dataForm['name'],
                    dataForm['description'],
                    dataForm['quantity'],
                    dataForm['unit'],
                    dataForm['minimum_stock'],
                    dataForm['supplier_id']
                )
                cursor.execute(querySQL, valores)
                conexion_MySQLdb.commit()

                # Obtener el ID del material recién insertado
                material_id = cursor.lastrowid

                # Registrar movimiento de entrada
                user_id = session.get('id')  # Obtener el ID del usuario desde la sesión
                queryMovimiento = """
                    INSERT INTO inventory_movements (material_id, quantity, movement_type, user_id)
                    VALUES (%s, %s, 'Entrada', %s)
                """
                cursor.execute(queryMovimiento, (material_id, dataForm['quantity'], user_id))
                conexion_MySQLdb.commit()

                return cursor.rowcount
    except Exception as e:
        print(f"Error en procesar_form_material: {e}")
        return []

def actualizar_stock(id, cantidad, tipo_movimiento):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                if tipo_movimiento == 'Entrada':
                    querySQL = "UPDATE materials SET quantity = quantity + %s WHERE id = %s"
                elif tipo_movimiento == 'Salida':
                    querySQL = "UPDATE materials SET quantity = quantity - %s WHERE id = %s"
                cursor.execute(querySQL, (cantidad, id))
                conexion_MySQLdb.commit()

                # Registrar movimiento de inventario
                user_id = session.get('id')  # Obtener el ID del usuario desde la sesión
                queryMovimiento = """
                    INSERT INTO inventory_movements (material_id, quantity, movement_type, user_id)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(queryMovimiento, (id, cantidad, tipo_movimiento, user_id))
                conexion_MySQLdb.commit()

                # Verificar y generar alertas después de actualizar el stock
                verificar_y_generar_alertas()

                return cursor.rowcount
    except Exception as e:
        print(f"Error en actualizar_stock: {e}")
        return []

def obtenerMaterial(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM materials WHERE id = %s"
                cursor.execute(querySQL, (id,))
                material = cursor.fetchone()
                return material
    except Exception as e:
        print(f"Error en obtenerMaterial: {e}")
        return []

def obtenerProveedores():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM suppliers"
                cursor.execute(querySQL)
                proveedores = cursor.fetchall()
                return proveedores
    except Exception as e:
        print(f"Error en obtenerProveedores: {e}")
        return []

def procesar_form_proveedor(dataForm):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    INSERT INTO suppliers (name, address, phone, email)
                    VALUES (%s, %s, %s, %s)
                """
                valores = (
                    dataForm['name'],
                    dataForm['address'],
                    dataForm['phone'],
                    dataForm['email']
                )
                cursor.execute(querySQL, valores)
                conexion_MySQLdb.commit()
                return cursor.rowcount
    except Exception as e:
        print(f"Error en procesar_form_proveedor: {e}")
        return []

def procesar_form_alerta(dataForm):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    INSERT INTO stock_alerts (material_id, minimum_stock)
                    VALUES (%s, %s)
                """
                valores = (
                    dataForm['material_id'],
                    dataForm['minimum_stock']
                )
                cursor.execute(querySQL, valores)
                conexion_MySQLdb.commit()
                return cursor.rowcount
    except Exception as e:
        print(f"Error en procesar_form_alerta: {e}")
        return []
    
def verificar_y_generar_alertas():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                # Obtener todos los materiales y sus niveles mínimos de stock
                querySQL = """
                    SELECT m.id, m.name, m.quantity, sa.minimum_stock
                    FROM materials m
                    JOIN stock_alerts sa ON m.id = sa.material_id
                    WHERE sa.alert_active = TRUE
                """
                cursor.execute(querySQL)
                materiales = cursor.fetchall()
                
                # Verificar si el stock está por debajo del nivel mínimo
                for material in materiales:
                    if material['quantity'] < material['minimum_stock']:
                        # Generar alerta
                        print(f"Alerta: El stock del material '{material['name']}' está por debajo del nivel mínimo.")
                        # Aquí puedes añadir la lógica para enviar notificaciones, por ejemplo, por correo electrónico o en la aplicación
    except Exception as e:
        print(f"Error en verificar_y_generar_alertas: {e}")

def obtenerMovimientos():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT im.id, m.name AS material_name, im.quantity, im.movement_type, im.date, u.name_surname AS user_name
                    FROM inventory_movements im
                    JOIN materials m ON im.material_id = m.id
                    JOIN users u ON im.user_id = u.id
                    ORDER BY im.date DESC
                """
                cursor.execute(querySQL)
                movimientos = cursor.fetchall()
                return movimientos
    except Exception as e:
        print(f"Error en obtenerMovimientos: {e}")
        return []