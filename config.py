# =================== Archivo de Configuración ===================
#
# Este archivo, `config.py`, se utilizará en el futuro para centralizar
# todas las variables de configuración de la aplicación AgroGrid.
#
# Propósitos principales:
# 1.  **Seguridad:** Almacenar datos sensibles como claves secretas (SECRET_KEY),
#     credenciales de base de datos y claves de API fuera del código fuente principal.
#     Idealmente, estos valores se cargarán desde variables de entorno.
#
# 2.  **Mantenibilidad:** Tener un único lugar para cambiar parámetros como la
#     configuración del correo, la URL de la base de datos o el número de
#     elementos por página.
#
# 3.  **Flexibilidad de Entornos:** Permitir diferentes configuraciones para
#     desarrollo, pruebas (testing) y producción. Por ejemplo, usar una base de
#     datos SQLite en desarrollo y una PostgreSQL en producción.
#
# Cuando sea necesario, aquí se definirán clases de configuración que la
# aplicación podrá cargar al iniciarse.
