import matplotlib
matplotlib.use('Agg')  # Configurar matplotlib para usar el backend 'Agg'

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from conexion.conexionBD import connectionBD
import os
import matplotlib.pyplot as plt

def generar_reporte_inventario():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM materials"
                cursor.execute(querySQL)
                materiales = cursor.fetchall()

                # Obtener los 5 materiales más usados
                querySQL = """
                SELECT name, SUM(quantity) as total_quantity
                FROM materials
                GROUP BY name
                ORDER BY total_quantity DESC
                LIMIT 5
                """
                cursor.execute(querySQL)
                top_materiales = cursor.fetchall()

        # Crear un nuevo archivo PDF
        file_path = os.path.join(os.getcwd(), "reporte_inventario.pdf")
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(name='Title', parent=styles['Title'], alignment=1)

        # Título
        elements.append(Paragraph("Reporte de Inventario", title_style))

        # Datos
        data = [["ID", "Nombre", "Descripción", "Cantidad", "Unidad", "Proveedor", "Stock Mínimo"]]
        for material in materiales:
            data.append([
                material['id'],
                material['name'],
                material['description'],
                material['quantity'],
                material['unit'],
                material['supplier_id'],
                material['minimum_stock']
            ])

        # Tabla
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        # Gráfico de los 5 materiales más usados
        nombres = [material['name'] for material in top_materiales]
        cantidades = [material['total_quantity'] for material in top_materiales]

        plt.figure(figsize=(7, 4))  # Ajustar el tamaño de la figura
        plt.bar(nombres, cantidades, color='blue')
        plt.xlabel('Material')
        plt.ylabel('Cantidad Usada')
        plt.title('Materiales Más Usados')
        plt.tight_layout()

        # Guardar el gráfico como imagen
        grafico_path = os.path.join(os.getcwd(), "grafico_materiales.png")
        plt.savefig(grafico_path)
        plt.close()

        # Agregar el gráfico al PDF
        elements.append(Image(grafico_path, width=400, height=200))  # Ajustar el tamaño de la imagen

        # Construir el PDF
        doc.build(elements)
        return file_path
    except Exception as e:
        print(f"Error en generar_reporte_inventario: {e}")
        return None

def generar_reporte_ordenes():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM work_orders"
                cursor.execute(querySQL)
                ordenes = cursor.fetchall()

                # Obtener la cantidad de órdenes por tipo de servicio
                querySQL = """
                SELECT service_type, COUNT(*) as total
                FROM work_orders
                GROUP BY service_type
                """
                cursor.execute(querySQL)
                ordenes_por_tipo = cursor.fetchall()

        # Crear un nuevo archivo PDF
        file_path = os.path.join(os.getcwd(), "reporte_ordenes.pdf")
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(name='Title', parent=styles['Title'], alignment=1)

        # Título
        elements.append(Paragraph("Reporte de Órdenes de Trabajo", title_style))

        # Datos
        data = [["ID", "Cliente ID", "Tipo de Servicio", "Descripción", "Fecha de Entrega", "Monto", "Estado"]]
        for orden in ordenes:
            data.append([
                orden['id'],
                orden['client_id'],
                orden['service_type'],
                orden['description'],
                orden['delivery_date'],
                orden['amount'],
                orden['status']
            ])

        # Tabla
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)

        # Gráfico de órdenes por tipo de servicio
        tipos_servicio = [orden['service_type'] for orden in ordenes_por_tipo]
        cantidades = [orden['total'] for orden in ordenes_por_tipo]

        plt.figure(figsize=(6, 3))  # Ajustar el tamaño de la figura
        plt.bar(tipos_servicio, cantidades, color='green')
        plt.xlabel('Tipo de Servicio')
        plt.ylabel('Cantidad de Órdenes')
        plt.title('Órdenes por Tipo de Servicio')
        plt.tight_layout()

        # Guardar el gráfico como imagen
        grafico_path = os.path.join(os.getcwd(), "grafico_ordenes.png")
        plt.savefig(grafico_path)
        plt.close()

        # Agregar el gráfico al PDF
        elements.append(Image(grafico_path, width=400, height=200))  # Ajustar el tamaño de la imagen

        # Construir el PDF
        doc.build(elements)
        return file_path
    except Exception as e:
        print(f"Error en generar_reporte_ordenes: {e}")
        return None

def generar_copia_seguridad():
    try:
        # Crear un nuevo archivo PDF
        file_path = os.path.join(os.getcwd(), "copia_seguridad.pdf")
        doc = SimpleDocTemplate(file_path, pagesize=letter)
        elements = []

        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(name='Title', parent=styles['Title'], alignment=1)

        # Título
        elements.append(Paragraph("Copia de Seguridad", title_style))

        # Obtener los datos de los clientes
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM clients"
                cursor.execute(querySQL)
                clientes = cursor.fetchall()

        # Datos de clientes
        elements.append(Paragraph("Clientes", title_style))
        data_clientes = [["ID", "Nombre", "Dirección", "Teléfono", "Documento"]]
        for cliente in clientes:
            data_clientes.append([
                cliente['id'],
                cliente['name'],
                cliente['address'],
                cliente['phone'],
                cliente['documento']
            ])
        table_clientes = Table(data_clientes)
        table_clientes.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table_clientes)

        # Obtener los datos de las órdenes de trabajo
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM work_orders"
                cursor.execute(querySQL)
                ordenes = cursor.fetchall()

        # Datos de órdenes de trabajo
        elements.append(Paragraph("Órdenes de Trabajo", title_style))
        data_ordenes = [["ID", "Cliente ID", "Tipo de Servicio", "Descripción", "Fecha de Entrega", "Monto", "Estado"]]
        for orden in ordenes:
            data_ordenes.append([
                orden['id'],
                orden['client_id'],
                orden['service_type'],
                orden['description'],
                orden['delivery_date'],
                orden['amount'],
                orden['status']
            ])
        table_ordenes = Table(data_ordenes)
        table_ordenes.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table_ordenes)

        # Obtener los datos de los proveedores
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM suppliers"
                cursor.execute(querySQL)
                proveedores = cursor.fetchall()

        # Datos de proveedores
        elements.append(Paragraph("Proveedores", title_style))
        data_proveedores = [["ID", "Nombre", "Dirección", "Teléfono", "Email"]]
        for proveedor in proveedores:
            data_proveedores.append([
                proveedor['id'],
                proveedor['name'],
                proveedor['address'],
                proveedor['phone'],
                proveedor['email']
            ])
        table_proveedores = Table(data_proveedores)
        table_proveedores.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table_proveedores)

        # Obtener los datos de los materiales
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM materials"
                cursor.execute(querySQL)
                materiales = cursor.fetchall()

        # Datos de materiales
        elements.append(Paragraph("Materiales", title_style))
        data_materiales = [["ID", "Nombre", "Descripción", "Cantidad", "Unidad", "Stock Mínimo", "Proveedor ID"]]
        for material in materiales:
            data_materiales.append([
                material['id'],
                material['name'],
                material['description'],
                material['quantity'],
                material['unit'],
                material['minimum_stock'],
                material['supplier_id']
            ])
        table_materiales = Table(data_materiales)
        table_materiales.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table_materiales)

        # Construir el PDF
        doc.build(elements)
        return file_path
    except Exception as e:
        print(f"Error en generar_copia_seguridad: {e}")
        return None