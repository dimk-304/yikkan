# Yikkan

Sistema de control de asistencia con Django + DRF + PostgreSQL + reconocimiento facial.

## Stack

- Backend: Django 5 + Django REST Framework
- Base de datos: PostgreSQL 17
- Infraestructura: Docker, Docker Compose, Fly.io
- Reconocimiento facial: `face-recognition` + `dlib`

## Estructura Docker

- Desarrollo: `docker-compose.dev.yml`
- Produccion: `docker-compose.prod.yml`
- Imagen unica: `Dockerfile`

## Desarrollo local

### 1) Levantar entorno

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

La app queda disponible en:

- `http://127.0.0.1:8002/`

### 2) Migraciones

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py migrate
```

### 3) Crear superusuario (opcional)

```bash
docker compose -f docker-compose.dev.yml exec web python manage.py createsuperuser
```

### 4) Cargar datos de prueba (opcional)

```bash
docker compose -f docker-compose.dev.yml exec web python scripts/create_test_users.py
docker compose -f docker-compose.dev.yml exec web python scripts/populate_hierarchy.py
```

Opcional: define contraseñas por variables de entorno para evitar valores aleatorios:

```bash
docker compose -f docker-compose.dev.yml exec \
  -e DEMO_ADMIN_PASSWORD='tu_password_admin' \
  -e DEMO_EMPLOYEE_PASSWORD='tu_password_empleado' \
  web python -m scripts.create_test_users

docker compose -f docker-compose.dev.yml exec \
  -e DEMO_HIERARCHY_PASSWORD='tu_password_jerarquia' \
  web python -m scripts.populate_hierarchy
```

### 5) Logs

```bash
docker compose -f docker-compose.dev.yml logs -f web
```

### 6) Detener entorno

```bash
docker compose -f docker-compose.dev.yml down
```

## Produccion con Docker Compose

1. Crear `.env.prod` desde el ejemplo:

```bash
cp .env.prod.example .env.prod
```

2. Levantar:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

3. Ejecutar migraciones:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

## Despliegue en VPS con SSL (Nginx + Certbot)

Esta seccion integra la guia operativa de despliegue tradicional fuera de Fly.

### 1) Preparacion

- Asegurate de estar en la carpeta raiz del proyecto en el servidor.
- Crea y edita `.env.prod`:

```bash
cp .env.prod.example .env.prod
nano .env.prod
```

Puntos minimos a revisar:

- `DJANGO_SECRET_KEY` seguro
- `POSTGRES_PASSWORD` seguro
- `ALLOWED_HOSTS` con tu dominio (`yikkan.com`, `www.yikkan.com`)

### 2) Primer despliegue SSL (paso inicial)

Como Nginx necesita certificados para levantar HTTPS y Certbot necesita Nginx para validar, haz este flujo:

1. Edita `nginx/conf.d/default.conf` y comenta temporalmente el bloque `server` de `443 ssl`.
2. Levanta Nginx en HTTP:

```bash
docker compose -f docker-compose.prod.yml up -d nginx
```

3. Solicita certificados:

```bash
docker compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path /var/www/certbot -d yikkan.com -d www.yikkan.com
```

4. Vuelve a `nginx/conf.d/default.conf` y descomenta el bloque SSL.

### 3) Despliegue final

```bash
docker compose -f docker-compose.prod.yml down
docker compose -f docker-compose.prod.yml up -d --build
```

### 4) Verificacion y mantenimiento

- Verifica `https://yikkan.com`.
- Revisa logs:

```bash
docker compose -f docker-compose.prod.yml logs -f
```

- Renovacion manual de certificados:

```bash
docker compose -f docker-compose.prod.yml run --rm certbot renew
```

## Deploy en Fly.io

El deploy usa `fly.toml` y el `Dockerfile` de la raiz.

Comandos utiles:

```bash
fly apps create yikkan
fly deploy
```

Si usas Postgres administrado en Fly, adjuntalo para inyectar `DATABASE_URL`:

```bash
fly postgres attach --app yikkan <nombre-del-cluster>
```

## Notas importantes

- Este proyecto usa `setuptools<82` para compatibilidad con `face_recognition_models`.
- Si tienes otro servicio ocupando el puerto 8000 en tu maquina, usa `8002` como esta configurado en dev.
