from app import app
from flask import render_template, request, flash, redirect, url_for, session, jsonify
from mysql.connector.errors import Error

# Importando conexión a BD
from controllers.funciones_home import *
from controllers.funciones_inventario import *
from controllers.funciones_reportes import generar_reporte_inventario, generar_reporte_ordenes
from controllers.funciones_reportes import generar_copia_seguridad

PATH_URL_INVENTARIO = "public/inventario"

@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        if session.get('role_id') == 1:  # Verificar si el usuario es administrador
            resp_usuariosBD = lista_usuariosBD()
            return render_template('public/usuarios/lista_usuarios.html', resp_usuariosBD=resp_usuariosBD)
        else:
            flash('No tienes permiso para acceder a esta página.', 'error')
            return redirect(url_for('inicio'))
    else:
        return redirect(url_for('inicio'))

@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))

@app.route('/asignar-rol', methods=['POST'])
def asignarRol():
    if 'conectado' in session and session.get('role_id') == 1:  # Verificar si el usuario es administrador
        user_id = request.form['user_id']
        role_id = request.form['role_id']
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    querySQL = "UPDATE users SET role_id = %s WHERE id = %s"
                    cursor.execute(querySQL, (role_id, user_id))
                    conexion_MySQLdb.commit()
                    flash('El rol fue asignado correctamente.', 'success')
        except Exception as e:
            flash(f"Error al asignar el rol: {e}", 'error')
        return redirect(url_for('usuarios'))
    else:
        flash('No tienes permiso para realizar esta acción.', 'error')
        return redirect(url_for('inicio'))

from app import app
from flask import render_template, request, flash, redirect, url_for, session
from controllers.funciones_home import *

@app.route('/registrar-orden', methods=['GET'])
def viewFormOrden():
    if 'conectado' in session:
        if session.get('role_id') == 1 or session.get('role_id') == 2:  # Verificar si el usuario es administrador
            clientes = obtenerClientes()
            materiales = obtenerMateriales()
            return render_template('public/ordenes/form_orden.html', clientes=clientes, materiales=materiales)
        else:
            flash('No tienes permiso para acceder a esta página.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/form-registrar-orden', methods=['POST'])
def formOrden():
    if 'conectado' in session:
        if session.get('role_id') == 1 or session.get('role_id') == 2:  # Verificar si el usuario es administrador
            dataForm = request.form.to_dict(flat=False)
            dataForm['status'] = 'Pendiente'  # Establecer el estado por defecto como "Pendiente"
            resultado = procesar_form_orden(dataForm)
            if resultado:
                flash('La orden de trabajo fue registrada correctamente.', 'success')
                return render_template('public/ordenes/form_orden.html', mostrar_modal=True, order_id=resultado)
            else:
                flash('La orden de trabajo NO fue registrada.', 'error')
                clientes = obtenerClientes()
                materiales = obtenerMateriales()
                return render_template('public/ordenes/form_orden.html', clientes=clientes, materiales=materiales)
        else:
            flash('No tienes permiso para acceder a esta página.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/confirmar-impresion/<int:order_id>', methods=['GET'])
def confirmar_impresion(order_id):
    return render_template('public/ordenes/confirmar_impresion.html', order_id=order_id)

@app.route('/imprimir-orden/<int:order_id>', methods=['GET'])
def imprimir_orden(order_id):
    orden = obtenerOrdenPorId(order_id)
    return render_template('public/ordenes/imprimir_orden.html', orden=orden)

@app.route('/lista-de-ordenes', methods=['GET'])
def lista_ordenes():
    if 'conectado' in session:
        if session.get('role_id') == 1 or session.get('role_id') == 2:  # Verificar si el usuario es administrador
            ordenes = obtenerOrdenes()
            # Asegúrate de que todas las órdenes tengan un estado válido
            for orden in ordenes:
                if orden['status'] is None:
                    orden['status'] = 'Pendiente'
            # Contar las órdenes por estado
            estados = {
                'Pendiente': len([o for o in ordenes if o['status'] == 'Pendiente']),
                'En Proceso': len([o for o in ordenes if o['status'] == 'En Proceso']),
                'Completado': len([o for o in ordenes if o['status'] == 'Completado']),
                'Entregado': len([o for o in ordenes if o['status'] == 'Entregado']),
                'Cancelado': len([o for o in ordenes if o['status'] == 'Cancelado'])
            }
            return render_template('public/ordenes/lista_ordenes.html', ordenes=ordenes, estados=estados)
        else:
            flash('No tienes permiso para acceder a esta página.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/gestionar-ordenes', methods=['GET'])
def gestionar_ordenes():
    if 'conectado' in session:
        if session.get('role_id') == 1 or session.get('role_id') == 2:  # Verificar si el usuario es administrador
            ordenes = obtenerOrdenes()
            return render_template('public/ordenes/gestionar_ordenes.html', ordenes=ordenes)
        else:
            flash('No tienes permiso para acceder a esta página.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/actualizar-estado-orden', methods=['POST'])
def actualizarEstadoOrden():
    if 'conectado' in session:
        order_id = request.form['order_id']
        new_status = request.form['status']
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    querySQL = "UPDATE work_orders SET status = %s WHERE id = %s"
                    cursor.execute(querySQL, (new_status, order_id))
                    conexion_MySQLdb.commit()
                    flash('El estado de la orden fue actualizado correctamente.', 'success')
        except Exception as e:
            flash(f"Error al actualizar el estado de la orden: {e}", 'error')
        return redirect(url_for('gestionar_ordenes'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/cancelar-orden', methods=['POST'])
def cancelarOrden():
    if 'conectado' in session:
        order_id = request.form['order_id']
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    querySQL = "UPDATE work_orders SET status = 'Cancelado' WHERE id = %s"
                    cursor.execute(querySQL, (order_id,))
                    conexion_MySQLdb.commit()
                    flash('La orden de trabajo fue cancelada correctamente.', 'success')
        except Exception as e:
            flash(f"Error al cancelar la orden de trabajo: {e}", 'error')
        return redirect(url_for('gestionar_ordenes'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/registrar-cliente', methods=['GET'])
def viewFormCliente():
    if 'conectado' in session:
        if session.get('role_id') == 1 or session.get('role_id') == 2:  # Verificar si el usuario es administrador
            return render_template('public/clientes/form_cliente.html')
        else:
           flash('No tienes permiso para acceder a esta página.', 'error')
        return redirect(url_for('inicio')) 
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/form-registrar-cliente', methods=['POST'])
def formCliente():
    if 'conectado' in session:
        resultado = procesar_form_cliente(request.form)
        if resultado:
            flash('El cliente fue registrado correctamente.', 'success')
            return redirect(url_for('lista_clientes'))
        else:
            flash('El cliente fue registrado.', 'success')
            return render_template('public/clientes/form_cliente.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/lista-de-clientes', methods=['GET'])
def lista_clientes():
    if 'conectado' in session:
        if session.get('role_id') == 1 or session.get('role_id') == 2:  # Verificar si el usuario es administrador
            clientes = obtenerClientes()
            return render_template('public/clientes/lista_clientes.html', clientes=clientes)
        else:
            flash('No tienes permiso para acceder a esta página.', 'error')
        return redirect(url_for('inicio')) 
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route('/borrar-cliente/<int:id>', methods=['GET'])
def borrarCliente(id):
    if 'conectado' in session:
        resultado = eliminarCliente(id)
        if resultado:
            flash('El cliente fue eliminado correctamente.', 'success')
        else:
            flash('Error, El cliente NO fue eliminado.', 'error')
        return redirect(url_for('listaClientes'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Rutas del módulo de inventario

@app.route('/inventario', methods=['GET'])
def consultar_stock():
    if 'conectado' in session:
        materiales = obtenerMateriales()
        return render_template(f'{PATH_URL_INVENTARIO}/consultar_stock.html', materiales=materiales)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/añadir-material', methods=['GET', 'POST'])
def añadir_material():
    if 'conectado' in session:
        if request.method == 'POST':
            dataForm = request.form.to_dict()
            resultado = procesar_form_material(dataForm)
            if resultado:
                flash('El material fue añadido correctamente.', 'success')
                return redirect(url_for('consultar_stock'))
            else:
                flash('El material NO fue añadido.', 'error')
        proveedores = obtenerProveedores()
        return render_template(f'{PATH_URL_INVENTARIO}/form_material.html', proveedores=proveedores)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/modificar-stock/<int:id>', methods=['GET', 'POST'])
def modificar_stock(id):
    if 'conectado' in session:
        if request.method == 'POST':
            cantidad = request.form['cantidad']
            tipo_movimiento = request.form['tipo_movimiento']
            resultado = actualizar_stock(id, cantidad, tipo_movimiento)
            if resultado:
                flash('El stock fue actualizado correctamente.', 'success')
                return redirect(url_for('consultar_stock'))
            else:
                flash('El stock NO fue actualizado.', 'error')
        material = obtenerMaterial(id)
        return render_template(f'{PATH_URL_INVENTARIO}/modificar_stock.html', material=material)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/gestionar-proveedores', methods=['GET', 'POST'])
def gestionar_proveedores():
    if 'conectado' in session:
        if request.method == 'POST':
            dataForm = request.form.to_dict()
            resultado = procesar_form_proveedor(dataForm)
            if resultado:
                flash('El proveedor fue gestionado correctamente.', 'success')
                return redirect(url_for('gestionar_proveedores'))
            else:
                flash('El proveedor NO fue gestionado.', 'error')
        proveedores = obtenerProveedores()
        return render_template(f'{PATH_URL_INVENTARIO}/gestionar_proveedores.html', proveedores=proveedores)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/establecer-alertas', methods=['GET', 'POST'])
def establecer_alertas():
    if 'conectado' in session:
        if request.method == 'POST':
            dataForm = request.form.to_dict()
            resultado = procesar_form_alerta(dataForm)
            if resultado:
                flash('La alerta fue establecida correctamente.', 'success')
                return redirect(url_for('consultar_stock'))
            else:
                flash('La alerta NO fue establecida.', 'error')
        materiales = obtenerMateriales()
        return render_template(f'{PATH_URL_INVENTARIO}/establecer_alertas.html', materiales=materiales)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/copia-seguridad', methods=['GET'])
def copia_seguridad():
    if 'conectado' in session:
        try:
            # Generar el archivo de copia de seguridad
            file_path = generar_copia_seguridad()
            if file_path:
                return send_file(file_path, as_attachment=True)
            else:
                flash('Error al generar la copia de seguridad.', 'error')
                return redirect(url_for('inicio'))
        except Exception as e:
            flash(f'Error al generar la copia de seguridad: {e}', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route('/movimientos', methods=['GET'])
def consultar_movimientos():
    if 'conectado' in session:
        movimientos = obtenerMovimientos()
        return render_template(f'{PATH_URL_INVENTARIO}/consultar_movimientos.html', movimientos=movimientos)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route('/reportes', methods=['GET'])
def vista_reportes():
    if 'conectado' in session:
        return render_template('public/reportes/vista_reportes.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/reporte-inventario', methods=['GET'])
def reporte_inventario():
    file_path = generar_reporte_inventario()
    if file_path:
        return send_file(file_path, as_attachment=True, download_name="reporte_inventario.pdf")
    else:
        flash('Error al generar el reporte de inventario.', 'error')
        return redirect(url_for('inicio'))

@app.route('/reporte-ordenes', methods=['GET'])
def reporte_ordenes():
    file_path = generar_reporte_ordenes()
    if file_path:
        return send_file(file_path, as_attachment=True, download_name="reporte_ordenes.pdf")
    else:
        flash('Error al generar el reporte de órdenes.', 'error')
        return redirect(url_for('inicio'))
    

# @app.route('/inicio', methods=['GET'])
# def principal():
#     if 'conectado' in session:
#         alertas_ordenes = generar_alertas()
#         alertas_stock = generar_alertas_stock()

#         return render_template('public/base_cpanel.html', alertas_ordenes=alertas_ordenes, 
#                                                           alertas_stock=alertas_stock)
#     else:
#         flash('Primero debes iniciar sesión.', 'error')
#         return redirect(url_for('login'))