# Historial de Contexto del Proyecto

## Reglas del Proyecto
1. **Idioma**: Comunicación totalmente en español.
2. **Código**: Términos técnicos y código en inglés.
3. **Documentación**: Mantener este historial actualizado para facilitar el retorno al proyecto.

## Descripción del Proyecto
**uz-checkpoint** es un sistema de control de asistencia mediante reconocimiento facial. Permite a los empleados registrar su entrada y salida utilizando la cámara del dispositivo para detectar su rostro.

## Stack Tecnológico
- **Backend**: Django 5.2.8 + Django REST Framework
- **Base de Datos**: PostgreSQL 17
- **Reconocimiento Facial**: face-recognition + dlib
- **Infraestructura**: Docker + docker-compose
- **Python**: 3.12

## Registro de Sesiones

### [2025-11-22] Implementación Completa del Backend
- **Estado**: Backend funcional con API REST.
- **Acciones Completadas**:
  1. Configuración del entorno Docker (Django + PostgreSQL 17).
  2. Creación de la app `attendance` con modelos:
     - `Employee`: Almacena datos del empleado y su encoding facial.
     - `AttendanceLog`: Registra entradas/salidas con timestamp.
  3. Implementación de lógica de reconocimiento facial en `utils.py`.
  4. Creación de endpoints API:
     - `POST /api/register/`: Registrar empleado con foto.
     - `POST /api/check/`: Verificar asistencia mediante foto.
  5. Migraciones aplicadas y servidor corriendo en `http://localhost:8000`.

## Endpoints Disponibles

### Registro de Empleado
```
POST /api/register/
Content-Type: multipart/form-data

Campos:
- first_name: string
- last_name: string
- email: string
- employee_id: string
- photo: file (imagen del rostro)
```

### Chequeo de Asistencia
```
POST /api/check/
Content-Type: multipart/form-data

Campos:
- photo: file (imagen del rostro para validar)

Respuesta exitosa:
- Identifica al empleado
- Registra CHECK_IN o CHECK_OUT automáticamente
```

## Próximos Pasos Sugeridos
- [ ] Crear interfaz web/móvil para captura de fotos
- [ ] Implementar panel de administración
- [ ] Agregar reportes de asistencia
- [ ] Mejorar tolerancia y precisión del reconocimiento
