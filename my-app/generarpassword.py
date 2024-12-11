from werkzeug.security import generate_password_hash

# Reemplaza 'tu_contraseña' con la contraseña que deseas encriptar
password = 'admin'
hashed_password = generate_password_hash(password, method='scrypt')

print(hashed_password)