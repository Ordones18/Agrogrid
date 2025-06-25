# =================== Importaciones de terceros ===================
from itsdangerous import URLSafeTimedSerializer  # Herramienta para generar y verificar tokens seguros con límite de tiempo.
from flask import current_app  # Proxy para acceder a la configuración de la aplicación Flask actual.

# =================== Utilidades de Token ===================

def generate_token(email):
    """
    Genera un token de seguridad con límite de tiempo para un correo electrónico específico.
    
    Este token se utiliza comúnmente para enlaces de confirmación de correo electrónico o
    restablecimiento de contraseña, ya que incrusta la información del email de forma segura.

    Args:
        email (str): El correo electrónico que se va a incluir en el token.

    Returns:
        str: El token serializado y seguro.
    """
    # Se crea una instancia del serializador usando la SECRET_KEY de la app para firmar el token.
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    # Se genera el token (dumps) incluyendo el email y una 'salt' para mayor seguridad.
    # La 'salt' asegura que este token solo sea válido para este propósito ('recover-password').
    return serializer.dumps(email, salt='recover-password')

def confirm_token(token, expiration=3600):
    """
    Verifica un token de seguridad y extrae el correo electrónico si es válido y no ha expirado.

    Args:
        token (str): El token que se va a verificar.
        expiration (int, optional): El tiempo máximo de vida del token en segundos. 
                                  Por defecto es 3600 (1 hora).

    Returns:
        str or bool: El correo electrónico si el token es válido, o False si ha expirado o es inválido.
    """
    # Se crea una instancia del serializador con la misma SECRET_KEY usada para generar el token.
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        # Se intenta cargar (loads) el token, verificando la firma, la 'salt' y el tiempo de expiración.
        email = serializer.loads(
            token, 
            salt='recover-password', 
            max_age=expiration
        )
    except Exception:
        # Si itsdangerous lanza cualquier excepción (firma inválida, token expirado, etc.), se retorna False.
        return False
    # Si la verificación es exitosa, se devuelve el correo electrónico contenido en el token.
    return email
