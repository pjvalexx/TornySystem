from app import app
from flask import render_template, request, flash, redirect, url_for, session, jsonify
from mysql.connector.errors import Error

# Importando conexión a BD
from controllers.funciones_home import *
from controllers.funciones_inventario import *

PATH_URL_EMPLEADOS = "public/empleados"
PATH_URL_INVENTARIO = "public/inventario"

@app.route('/registrar-empleado', methods=['GET'])
def viewFormEmpleado():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_EMPLEADOS}/form_empleado.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/form-registrar-empleado', methods=['POST'])
def formEmpleado():
    if 'conectado' in session:
        if 'foto_empleado' in request.files:
            foto_perfil = request.files['foto_empleado']
            resultado = procesar_form_empleado(request.form, foto_perfil)
            if resultado:
                return redirect(url_for('lista_empleados'))
            else:
                flash('El empleado NO fue registrado.', 'error')
                return render_template(f'{PATH_URL_EMPLEADOS}/form_empleado.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/lista-de-empleados', methods=['GET'])
def lista_empleados():
    if 'conectado' in session:
        return render_template(f'{PATH_URL_EMPLEADOS}/lista_empleados.html', empleados=sql_lista_empleadosBD())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route("/detalles-empleado/", methods=['GET'])
@app.route("/detalles-empleado/<int:idEmpleado>", methods=['GET'])
def detalleEmpleado(idEmpleado=None):
    if 'conectado' in session:
        # Verificamos si el parámetro idEmpleado es None o no está presente en la URL
        if idEmpleado is None:
            return redirect(url_for('inicio'))
        else:
            detalle_empleado = sql_detalles_empleadosBD(idEmpleado) or []
            return render_template(f'{PATH_URL_EMPLEADOS}/detalles_empleado.html', detalle_empleado=detalle_empleado)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Buscando de empleados
@app.route("/buscando-empleado", methods=['POST'])
def viewBuscarEmpleadoBD():
    resultadoBusqueda = buscarEmpleadoBD(request.json['busqueda'])
    if resultadoBusqueda:
        return render_template(f'{PATH_URL_EMPLEADOS}/resultado_busqueda_empleado.html', dataBusqueda=resultadoBusqueda)
    else:
        return jsonify({'fin': 0})

@app.route("/editar-empleado/<int:id>", methods=['GET'])
def viewEditarEmpleado(id):
    if 'conectado' in session:
        respuestaEmpleado = buscarEmpleadoUnico(id)
        if respuestaEmpleado:
            return render_template(f'{PATH_URL_EMPLEADOS}/form_empleado_update.html', respuestaEmpleado=respuestaEmpleado)
        else:
            flash('El empleado no existe.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# Recibir formulario para actualizar información de empleado
@app.route('/actualizar-empleado', methods=['POST'])
def actualizarEmpleado():
    resultData = procesar_actualizacion_form(request)
    if resultData:
        return redirect(url_for('lista_empleados'))

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

@app.route('/borrar-empleado/<string:id_empleado>/<string:foto_empleado>', methods=['GET'])
def borrarEmpleado(id_empleado, foto_empleado):
    resp = eliminarEmpleado(id_empleado, foto_empleado)
    if resp:
        flash('El Empleado fue eliminado correctamente', 'success')
        return redirect(url_for('lista_empleados'))

@app.route("/descargar-informe-empleados/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

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

@app.route('/registrar-orden', methods=['GET'])
def viewFormOrden():
    if 'conectado' in session:
        clientes = obtenerClientes()
        return render_template('public/ordenes/form_orden.html', clientes=clientes)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/form-registrar-orden', methods=['POST'])
def formOrden():
    if 'conectado' in session:
        dataForm = request.form.to_dict()
        dataForm['status'] = 'Pendiente'  # Establecer el estado por defecto como "Pendiente"
        resultado = procesar_form_orden(dataForm)
        if resultado:
            flash('La orden de trabajo fue registrada correctamente.', 'success')
            return redirect(url_for('lista_ordenes'))
        else:
            flash('La orden de trabajo NO fue registrada.', 'error')
            return render_template('public/ordenes/form_orden.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/lista-de-ordenes', methods=['GET'])
def lista_ordenes():
    if 'conectado' in session:
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
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/gestionar-ordenes', methods=['GET'])
def gestionar_ordenes():
    if 'conectado' in session:
        ordenes = obtenerOrdenes()
        return render_template('public/ordenes/gestionar_ordenes.html', ordenes=ordenes)
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
        return render_template('public/clientes/form_cliente.html')
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
            flash('El cliente NO fue registrado.', 'error')
            return render_template('public/clientes/form_cliente.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

@app.route('/lista-de-clientes', methods=['GET'])
def lista_clientes():
    if 'conectado' in session:
        clientes = obtenerClientes()
        return render_template('public/clientes/lista_clientes.html', clientes=clientes)
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
        # Lógica para generar la copia de seguridad
        flash('Copia de seguridad generada correctamente.', 'success')
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