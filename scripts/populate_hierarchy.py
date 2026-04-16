#!/usr/bin/env python
"""
Script para poblar jerarquia organizacional de prueba.
Ejecutar con:
docker compose -f docker-compose.dev.yml exec web python scripts/populate_hierarchy.py
"""
import os
import secrets

import django

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uz_checkpoint.settings')
django.setup()

from attendance.models import Employee


def _hierarchy_password() -> str:
    return os.getenv("DEMO_HIERARCHY_PASSWORD", secrets.token_urlsafe(12))


def create_hierarchy():
    print("🚀 Iniciando creación de jerarquía organizacional...")
    default_password = _hierarchy_password()

    # 1. Crear CEO
    ceo, created = Employee.objects.get_or_create(
        employee_id="CEO-001",
        defaults={
            "first_name": "Roberto",
            "last_name": "Dueñas",
            "email": "ceo@uz.com",
            "role": "CEO",
            "position": "Chief Executive Officer",
            "department": "Dirección General",
            "username": "ceo",
            "is_active": True,
        },
    )
    if created:
        ceo.set_password(default_password)
        ceo.save()
        print(f"✅ CEO creado: {ceo}")
    else:
        print(f"ℹ️ CEO ya existe: {ceo}")

    # 2. Crear Directores (Reportan al CEO)
    directors_data = [
        ("Ana", "García", "DIR-001", "Operaciones"),
        ("Carlos", "López", "DIR-002", "Tecnología"),
    ]

    directors = []
    for first, last, emp_id, dept in directors_data:
        dir_obj, created = Employee.objects.get_or_create(
            employee_id=emp_id,
            defaults={
                "first_name": first,
                "last_name": last,
                "email": f"{first.lower()}.{last.lower()}@uz.com",
                "role": "DIRECTOR",
                "position": f"Director de {dept}",
                "department": dept,
                "supervisor": ceo,
                "username": f"dir.{first.lower()}",
                "is_active": True,
            },
        )
        if created:
            dir_obj.set_password(default_password)
            dir_obj.save()
            print(f"  ✅ Director creado: {dir_obj} (Supervisor: {ceo.first_name})")
        directors.append(dir_obj)

    # 3. Crear Gerentes (Reportan a Directores)
    managers = []
    for director in directors:
        for i in range(2):  # 2 gerentes por director
            first = f"Gerente{i+1}"
            last = f"De{director.first_name}"
            emp_id = f"MGR-{director.id}-{i}"

            mgr, created = Employee.objects.get_or_create(
                employee_id=emp_id,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": f"gerente.{director.id}.{i}@uz.com",
                    "role": "MANAGER",
                    "position": "Gerente de Área",
                    "department": director.department,
                    "supervisor": director,
                    "username": f"mgr.{director.id}.{i}",
                    "is_active": True,
                },
            )
            if created:
                mgr.set_password(default_password)
                mgr.save()
                print(f"    ✅ Gerente creado: {mgr} (Supervisor: {director.first_name})")
            managers.append(mgr)

    # 4. Crear Operadores (Reportan a Gerentes)
    for manager in managers:
        for i in range(3):  # 3 operadores por gerente
            first = f"Operador{i+1}"
            last = f"De{manager.first_name}"
            emp_id = f"OP-{manager.id}-{i}"

            op, created = Employee.objects.get_or_create(
                employee_id=emp_id,
                defaults={
                    "first_name": first,
                    "last_name": last,
                    "email": f"op.{manager.id}.{i}@uz.com",
                    "role": "OPERATOR",
                    "position": "Operador",
                    "department": manager.department,
                    "supervisor": manager,
                    "username": f"op.{manager.id}.{i}",
                    "is_active": True,
                },
            )
            if created:
                op.set_password(default_password)
                op.save()
                print(f"      ✅ Operador creado: {op} (Supervisor: {manager.first_name})")

    print("\n✨ Jerarquía creada exitosamente.")
    print("Credenciales de esta ejecución:")
    print(f"- Password común de jerarquía: {default_password}")
    print("Tip: define DEMO_HIERARCHY_PASSWORD para contraseña fija.")


if __name__ == "__main__":
    create_hierarchy()
