# En hash_pass.py
from app.auth import get_password_hash

# Elige tu contraseña
password_plana = "admin123" 
hashed_password = get_password_hash(password_plana)

print("¡Usa este hash para tu base de datos!:")
print(f"'{hashed_password}'")