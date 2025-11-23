#!/usr/bin/env python
"""
Script para crear usuarios de prueba
Ejecutar con: docker-compose run web python create_test_users.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uz_checkpoint.settings')
django.setup()

from attendance.models import Employee

def create_test_users():
    # Crear admin
    admin, created = Employee.objects.get_or_create(
        username='admin',
        defaults={
            'first_name': 'Admin',
            'last_name': 'Sistema',
            'email': 'admin@uz-checkpoint.com',
            'employee_id': 'ADMIN001',
            'role': 'ADMIN',
            'is_active': True
        }
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"✅ Usuario admin creado - Username: admin, Password: admin123")
    else:
        print(f"ℹ️  Usuario admin ya existe")

    # Crear empleado de prueba
    employee, created = Employee.objects.get_or_create(
        username='empleado',
        defaults={
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'email': 'juan.perez@uz-checkpoint.com',
            'employee_id': 'EMP001',
            'role': 'EMPLOYEE',
            'is_active': True
        }
    )
    if created:
        employee.set_password('empleado123')
        employee.save()
        print(f"✅ Usuario empleado creado - Username: empleado, Password: empleado123")
    else:
        print(f"ℹ️  Usuario empleado ya existe")

if __name__ == '__main__':
    create_test_users()
    print("\n📋 Usuarios de prueba:")
    print("   Admin: username=admin, password=admin123")
    print("   Empleado: username=empleado, password=empleado123")
