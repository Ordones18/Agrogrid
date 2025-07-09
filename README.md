

## 4. Exponer con Tunnelmole

Para compartir tu servidor local con otros a través de internet, usa Tunnelmole.

1.  Abre una **nueva terminal** (deja la que ejecuta `run.py` abierta).
2.  Ejecuta el siguiente comando para crear un túnel hacia tu puerto 5000:
    ```bash
    npx tunnelmole 5000
    ```
3.  Tunnelmole te proporcionará una URL pública (ej. `https://xxxx.tunnelmole.net`).

### ¡ADVERTENCIA DE SEGURIDAD!

- **No compartas** la URL de Tunnelmole con personas desconocidas o en sitios públicos.
- Exponer tu servidor local, especialmente con el **modo de depuración activado (`debug=True`)**, es un **riesgo de seguridad grave**. Un atacante podría ejecutar código en tu computadora.
- Usa esta función solo para pruebas cortas y con personas de confianza.


