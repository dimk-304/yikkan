#!/usr/bin/env python
"""
Script para crear usuarios de prueba.
Ejecutar con:
docker compose -f docker-compose.dev.yml exec web python scripts/create_test_users.py
"""
import os
import secrets

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uz_checkpoint.settings')
django.setup()

from attendance.models import Employee


def _password_from_env_or_random(env_name: str) -> str:
    value = os.getenv(env_name)
    if value:
        return value
    return secrets.token_urlsafe(12)


def create_test_users():
    admin_password = _password_from_env_or_random('DEMO_ADMIN_PASSWORD')
    employee_password = _password_from_env_or_random('DEMO_EMPLOYEE_PASSWORD')

    # Crear admin
    admin, created = Employee.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Admin',
            'last_name': 'Sistema',
            'email': 'admin@uz-checkpoint.com',
            'employee_id': 'ADMIN001',
            'role': 'ADMIN',
            'is_active': True,
        },
    )
    admin.set_password(admin_password)
    admin.save()
    print("✅ Usuario admin listo - Username: admin")
    if not created:
        print("ℹ️  Usuario admin ya existía, contraseña actualizada en esta ejecución")

    # Crear empleado de prueba
    employee, created = Employee.objects.get_or_create(
        username='empleado',
        defaults={
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan.perez@uz-checkpoint.com',
            'employee_id': 'EMP001',
            'role': 'EMPLOYEE',
            'is_active': True,
        },
    )
    employee.set_password(employee_password)
    employee.save()
    print("✅ Usuario empleado listo - Username: empleado")
    if not created:
        print("ℹ️  Usuario empleado ya existía, contraseña actualizada en esta ejecución")

    return admin_password, employee_password


if __name__ == '__main__':
    admin_password, employee_password = create_test_users()
    print("\n📋 Usuarios de prueba:")
    print(f"   Admin: username=admin, password={admin_password}")
    print(f"   Empleado: username=empleado, password={employee_password}")
    print("\nTip: define DEMO_ADMIN_PASSWORD y DEMO_EMPLOYEE_PASSWORD para contraseñas fijas.")
