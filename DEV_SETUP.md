# 🚀 Instrucciones para levantar el entorno de desarrollo

## Requisitos previos
- **Docker** y **Docker Compose** instalados (versión 2.0+).
- **Python 3.12** (solo si deseas ejecutar scripts fuera del contenedor).
- Clonar el repositorio o tener la carpeta del proyecto en tu máquina.

## 1️⃣ Preparar variables de entorno
Copia el archivo de ejemplo y ajusta los valores si es necesario:
```bash
cp .env.example .env
# Edita .env si cambias la contraseña de la base de datos o el puerto
```
> El archivo `.env` contiene variables como `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` y `DJANGO_SECRET_KEY`.

## 2️⃣ Construir y levantar los contenedores
```bash
# Desde la raíz del proyecto (~/Desktop/uz-checkpoint)
cd /Users/dannycen/Desktop/uz-checkpoint

# Construye la imagen y levanta los servicios en segundo plano
docker-compose up -d --build
```
- El servicio **web** corre en `http://localhost:8000/`.
- El servicio **db** (PostgreSQL) corre en el contenedor `db` y está expuesto al interior de Docker.

## 3️⃣ Ejecutar migraciones y crear super‑usuario
```bash
# Ejecuta comandos dentro del contenedor web
docker-compose exec web python manage.py migrate

# (Opcional) Crear un super‑usuario para acceder al admin de Django
docker-compose exec web python manage.py createsuperuser
```
> Usa el mismo `username`/`password` que definiste al crear el super‑usuario.

## 4️⃣ Poblado de datos de prueba (opcional)
El proyecto incluye `create_test_users.py` para generar usuarios de prueba:
```bash
docker-compose exec web python create_test_users.py
```
Esto crea:
- **Admin**: `admin` / `admin123`
- **Empleado**: `empleado` / `empleado123`

## 5️⃣ Acceder a la aplicación
- **Login**: `http://localhost:8000/login`
- **Chequeo de asistencia**: `http://localhost:8000/attendance`
- **Dashboard admin** (solo admin): `http://localhost:8000/dashboard`
- **Panel de empleado** (solo empleado): `http://localhost:8000/employee-panel`

## 6️⃣ Detener y limpiar el entorno
```bash
# Detener los contenedores
docker-compose down

# (Opcional) Eliminar volúmenes para borrar la base de datos
docker-compose down -v
```
> Si eliminas los volúmenes perderás todos los datos almacenados en PostgreSQL.

## 7️⃣ Reconstruir después de cambios en dependencias o Dockerfile
```bash
docker-compose up -d --build
```

---
### Tips de desarrollo
- **Logs en tiempo real**: `docker-compose logs -f web`
- **Acceder al shell del contenedor**: `docker-compose exec web /bin/bash`
- **Ejecutar pruebas** (si añades tests): `docker-compose exec web python manage.py test`

Con estos pasos podrás levantar, usar y detener el entorno rápidamente. ¡Éxitos con el desarrollo! 🎉
