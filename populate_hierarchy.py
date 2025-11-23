import os
import django
import random

# Configurar entorno Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'uz_checkpoint.settings')
django.setup()

from attendance.models import Employee

def create_hierarchy():
    print("🚀 Iniciando creación de jerarquía organizacional...")
    
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
            "is_active": True
        }
    )
    if created:
        ceo.set_password("admin123")
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
                "is_active": True
            }
        )
        if created:
            dir_obj.set_password("admin123")
            dir_obj.save()
            print(f"  ✅ Director creado: {dir_obj} (Supervisor: {ceo.first_name})")
        directors.append(dir_obj)

    # 3. Crear Gerentes (Reportan a Directores)
    managers = []
    for director in directors:
        for i in range(2): # 2 gerentes por director
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
                    "is_active": True
                }
            )
            if created:
                mgr.set_password("1234")
                mgr.save()
                print(f"    ✅ Gerente creado: {mgr} (Supervisor: {director.first_name})")
            managers.append(mgr)

    # 4. Crear Operadores (Reportan a Gerentes)
    for manager in managers:
        for i in range(3): # 3 operadores por gerente
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
                    "is_active": True
                }
            )
            if created:
                op.set_password("1234")
                op.save()
                print(f"      ✅ Operador creado: {op} (Supervisor: {manager.first_name})")

    print("\n✨ Jerarquía creada exitosamente.")
    print("Usuarios de prueba:")
    print("- CEO: ceo / admin123")
    print("- Director: dir.ana / admin123")
    print("- Gerente: mgr.[id].0 / 1234")
    print("- Operador: op.[id].0 / 1234")

if __name__ == "__main__":
    create_hierarchy()
