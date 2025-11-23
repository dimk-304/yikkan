# 🚀 Guía de Despliegue para Yikkan.com

Sigue estos pasos para desplegar tu aplicación en producción con SSL (HTTPS).

## 1️⃣ Preparación en el Servidor
Asegúrate de estar en la carpeta del proyecto en tu servidor (VPS).

### Configurar Variables de Entorno
Crea el archivo `.env.prod` a partir del ejemplo:
```bash
cp .env.prod.example .env.prod
nano .env.prod
```
**IMPORTANTE:**
- Cambia `DJANGO_SECRET_KEY` por una cadena larga y aleatoria.
- Cambia `POSTGRES_PASSWORD` por una contraseña segura.
- Asegúrate de que `ALLOWED_HOSTS` incluya `yikkan.com` y `www.yikkan.com`.

## 2️⃣ Obtener Certificados SSL (Primer Despliegue)
Como Nginx necesita los certificados para arrancar, pero Certbot necesita Nginx para validar el dominio, debemos hacerlo en dos pasos.

### Paso A: Arrancar Nginx solo en HTTP
1. Edita `nginx/conf.d/default.conf`:
   ```bash
   nano nginx/conf.d/default.conf
   ```
2. **Comenta** (pon `#` al inicio) toda la sección del segundo bloque `server { listen 443 ssl; ... }`.
3. Guarda y sal.

### Paso B: Levantar Nginx
```bash
docker-compose -f docker-compose.prod.yml up -d nginx
```

### Paso C: Ejecutar Certbot
Ejecuta este comando para pedir el certificado:
```bash
docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path /var/www/certbot -d yikkan.com -d www.yikkan.com
```
- Te pedirá un email y aceptar términos.
- Si todo sale bien, dirá "Congratulations!".

### Paso D: Restaurar configuración SSL
1. Vuelve a editar `nginx/conf.d/default.conf`.
2. **Descomenta** la sección SSL que comentaste en el Paso A.
3. Guarda y sal.

## 3️⃣ Despliegue Final
Ahora que tienes los certificados y la configuración lista:

```bash
# Detener lo que esté corriendo
docker-compose -f docker-compose.prod.yml down

# Construir y levantar todo
docker-compose -f docker-compose.prod.yml up -d --build
```

## 4️⃣ Verificación
- Visita `https://yikkan.com`.
- Deberías ver el candado de seguridad 🔒.
- Prueba el login y la funcionalidad de la cámara.

## Mantenimiento
- **Renovar certificados:** Certbot intentará renovarlos, pero puedes forzarlo con:
  ```bash
  docker-compose -f docker-compose.prod.yml run --rm certbot renew
  ```
- **Ver logs:**
  ```bash
  docker-compose -f docker-compose.prod.yml logs -f
  ```
