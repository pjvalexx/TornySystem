-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         8.0.30 - MySQL Community Server - GPL
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.1.0.6537
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

-- Volcando estructura de base de datos para crud_python
CREATE DATABASE IF NOT EXISTS `torny_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `torny_db`;


-- Crear tabla de roles
CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- Crear tabla de usuarios con la columna role_id
CREATE TABLE users (
    id INT AUTO_INCREMENT,
    name_surname VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    email_user VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    pass_user TEXT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
    created_user TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    role_id INT,
    PRIMARY KEY (id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Insertar roles
INSERT INTO roles (name) VALUES ('Administrador'), ('WorkOrderCreator'), ('InventoryManager');

-- Volcando datos para la tabla users: ~1 row (aproximadamente)
INSERT INTO users (id, name_surname, email_user, pass_user, created_user, role_id) VALUES
    (1, 'admin', 'admin@gmail.com', 'scrypt:32768:8:1$F8yORQ9MIXyCow6h$9e8a15fde5141e1d78346699642ae84870b3e2a2ba194918e4038d241d5f71301c83222956077d0e1e8a5bc3225bbd94ae287d05856bb3f5a389a3c5e5be3c7b', '2023-07-21 20:10:01', 1);

-- Crear tabla de clientes
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL
);

-- Crear tabla de órdenes de trabajo
CREATE TABLE work_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    service_type ENUM('Fabricacion', 'Rectificacion', 'Reparacion') NOT NULL,
    description TEXT NOT NULL,
    delivery_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    status ENUM('Pendiente', 'En Proceso', 'Completado', 'Entregado', 'Cancelado') NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Crear tabla de proveedores
CREATE TABLE suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL
);

-- Crear tabla de materiales
CREATE TABLE materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    quantity INT NOT NULL,
    unit VARCHAR(20) NOT NULL,
    minimum_stock INT NOT NULL,
    supplier_id INT,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Crear tabla de movimientos de inventario
CREATE TABLE inventory_movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    material_id INT,
    quantity INT NOT NULL,
    movement_type ENUM('Entrada', 'Salida') NOT NULL,
    date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (material_id) REFERENCES materials(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Crear tabla de alertas de stock
CREATE TABLE stock_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    material_id INT,
    minimum_stock INT NOT NULL,
    alert_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES materials(id)
);

CREATE TABLE work_order_materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    work_order_id INT,
    material_id INT,
    quantity INT,
    FOREIGN KEY (work_order_id) REFERENCES work_orders(id),
    FOREIGN KEY (material_id) REFERENCES materials(id)
);
/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;