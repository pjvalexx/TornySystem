# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
from flask import session
import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD

import datetime
import re
import os

from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio


import openpyxl  # Para generar el excel
# biblioteca o modulo send_file para forzar la descarga
from flask import send_file


# Lista de Usuarios creados
def lista_usuariosBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id, name_surname, email_user, created_user, role_id FROM users"
                cursor.execute(querySQL,)
                usuariosBD = cursor.fetchall()
        return usuariosBD
    except Exception as e:
        print(f"Error en lista_usuariosBD : {e}")
        return []


# Eliminar uEmpleado
def eliminarEmpleado(id_empleado, foto_empleado):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tbl_empleados WHERE id_empleado=%s"
                cursor.execute(querySQL, (id_empleado,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount

                if resultado_eliminar:
                    # Eliminadon foto_empleado desde el directorio
                    basepath = path.dirname(__file__)
                    url_File = path.join(
                        basepath, '../static/fotos_empleados', foto_empleado)

                    if path.exists(url_File):
                        remove(url_File)  # Borrar foto desde la carpeta

        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarEmpleado : {e}")
        return []


# Eliminar usuario
def eliminarUsuario(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM users WHERE id=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount

        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarUsuario : {e}")
        return []


def procesar_form_cliente(dataForm):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                sql = """
                    INSERT INTO clients (name, address, phone)
                    VALUES (%s, %s, %s)
                """
                valores = (
                    dataForm['name'],
                    dataForm['address'],
                    dataForm['phone']
                )
                cursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                return cursor.rowcount
    except Exception as e:
        print(f"Error en procesar_form_cliente: {e}")
        return []

def obtenerClientes():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id, name, address, phone FROM clients"
                cursor.execute(querySQL)
                clientes = cursor.fetchall()
        return clientes
    except Exception as e:
        print(f"Error en obtenerClientes: {e}")
        return []

def procesar_form_orden(dataForm):
    try:
        print("Datos del formulario:", dataForm)  # Depuración
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                sql = """
                    INSERT INTO work_orders (client_id, service_type, description, delivery_date, amount, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                valores = (
                    dataForm['client_id'][0],
                    dataForm['service_type'][0],
                    dataForm['description'][0],
                    dataForm['delivery_date'][0],
                    dataForm['amount'][0],
                    dataForm['status']
                )
                print("Valores para insertar en work_orders:", valores)  # Depuración
                cursor.execute(sql, valores)
                conexion_MySQLdb.commit()

                # Obtener el ID de la orden de trabajo recién insertada
                order_id = cursor.lastrowid
                print("ID de la orden de trabajo recién insertada:", order_id)  # Depuración

                # Insertar materiales utilizados en la orden de trabajo
                for material_id in dataForm['materials[]']:
                    cantidad = dataForm['quantities[{}]'.format(material_id)][0]
                    sql_material = """
                        INSERT INTO work_order_materials (work_order_id, material_id, quantity)
                        VALUES (%s, %s, %s)
                    """
                    print("Insertando material:", (order_id, material_id, cantidad))  # Depuración
                    cursor.execute(sql_material, (order_id, material_id, cantidad))
                    conexion_MySQLdb.commit()

                    # Actualizar el stock del material
                    sql_update_stock = """
                        UPDATE materials
                        SET quantity = quantity - %s
                        WHERE id = %s
                    """
                    cursor.execute(sql_update_stock, (cantidad, material_id))
                    conexion_MySQLdb.commit()

                    # Registrar movimiento de inventario
                    user_id = session.get('id')  # Obtener el ID del usuario desde la sesión
                    queryMovimiento = """
                        INSERT INTO inventory_movements (material_id, quantity, movement_type, user_id)
                        VALUES (%s, %s, 'Salida', %s)
                    """
                    cursor.execute(queryMovimiento, (material_id, cantidad, user_id))
                    conexion_MySQLdb.commit()

                return order_id
    except Exception as e:
        print(f"Error en procesar_form_orden: {e}")
        return []
    
def obtenerOrdenPorId(order_id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT wo.id, wo.client_id, wo.service_type, wo.description, wo.delivery_date, wo.amount, wo.status,
                           c.name AS client_name, c.address AS client_address, c.phone AS client_phone
                    FROM work_orders wo
                    JOIN clients c ON wo.client_id = c.id
                    WHERE wo.id = %s
                """
                cursor.execute(querySQL, (order_id,))
                orden = cursor.fetchone()

                # Obtener los materiales utilizados en la orden de trabajo
                queryMaterials = """
                    SELECT wom.material_id, m.name, wom.quantity
                    FROM work_order_materials wom
                    JOIN materials m ON wom.material_id = m.id
                    WHERE wom.work_order_id = %s
                """
                cursor.execute(queryMaterials, (order_id,))
                materiales = cursor.fetchall()

                orden['materials'] = materiales
                return orden
    except Exception as e:
        print(f"Error en obtenerOrdenPorId: {e}")
        return None

def obtenerOrdenes():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                    SELECT wo.id, c.name AS client_name, wo.service_type, wo.description, wo.delivery_date, wo.amount, wo.status
                    FROM work_orders wo
                    JOIN clients c ON wo.client_id = c.id
                """
                cursor.execute(querySQL)
                ordenes = cursor.fetchall()
        return ordenes
    except Exception as e:
        print(f"Error en obtenerOrdenes: {e}")
        return []