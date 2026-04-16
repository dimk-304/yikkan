from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import json

class Employee(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('CEO', 'CEO'),
        ('DIRECTOR', 'Director'),
        ('MANAGER', 'Gerente'),
        ('OPERATOR', 'Operador'),
        ('EMPLOYEE', 'Empleado'),
    )
    
    # Información básica
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    employee_id = models.CharField(max_length=20, unique=True)
    photo = models.ImageField(upload_to='employees/')
    profile_photo = models.ImageField(upload_to='employees/profile/', null=True, blank=True)
    
    # Autenticación
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='EMPLOYEE')
    
    # Jerarquía organizacional
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates', help_text="Supervisor directo")
    department = models.CharField(max_length=100, null=True, blank=True, help_text="Departamento")
    position = models.CharField(max_length=100, null=True, blank=True, help_text="Título del puesto")
    
    # Reconocimiento facial
    face_encoding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Horarios de trabajo
    work_start_time = models.TimeField(null=True, blank=True, help_text="Hora de entrada")
    work_end_time = models.TimeField(null=True, blank=True, help_text="Hora de salida")
    lunch_start_time = models.TimeField(null=True, blank=True, help_text="Inicio de hora de comida")
    lunch_end_time = models.TimeField(null=True, blank=True, help_text="Fin de hora de comida")
    
    # Estado
    is_active = models.BooleanField(default=True, help_text="Empleado activo")
    is_superadmin = models.BooleanField(default=False, help_text="Permisos globales del sistema")

    def set_password(self, raw_password):
        """Hashea y guarda la contraseña"""
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        """Verifica la contraseña"""
        return check_password(raw_password, self.password)
    
    def get_subordinates(self):
        """Retorna todos los subordinados directos"""
        return self.subordinates.filter(is_active=True)
    
    def get_all_subordinates(self):
        """Retorna todos los subordinados (directos e indirectos) recursivamente"""
        subordinates = list(self.get_subordinates())
        for subordinate in list(subordinates):
            subordinates.extend(subordinate.get_all_subordinates())
        return subordinates
    
    def get_hierarchy_level(self):
        """Retorna el nivel en la jerarquía (0=CEO, 1=Director, etc.)"""
        role_levels = {
            'CEO': 0,
            'DIRECTOR': 1,
            'MANAGER': 2,
            'OPERATOR': 3,
            'EMPLOYEE': 4,
            'ADMIN': -1,  # Admin no está en jerarquía normal
        }
        return role_levels.get(self.role, 999)
    
    def can_manage(self, employee):
        """Verifica si puede gestionar a otro empleado"""
        if self.is_superadmin or self.role == 'ADMIN':
            return True
        # Puede gestionar si es su supervisor directo o está en su cadena de supervisión
        return employee in self.get_all_subordinates()

    def is_system_admin(self):
        """Compatibilidad: admin legacy por rol o nuevo flag de permisos"""
        return self.is_superadmin or self.role == 'ADMIN'
    
    def get_supervisor_chain(self):
        """Retorna la cadena de supervisores hasta el CEO"""
        chain = []
        current = self.supervisor
        while current:
            chain.append(current)
            current = current.supervisor
        return chain

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_id})"

class AttendanceLog(models.Model):
    TYPE_CHOICES = (
        ('CHECK_IN', 'Entrada'),
        ('CHECK_OUT', 'Salida'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return f"{self.employee} - {self.type} at {self.timestamp}"

class Incident(models.Model):
    """Modelo para incidencias reportadas por empleados"""
    TYPE_CHOICES = (
        ('ABSENCE', 'Falta'),
        ('LATE', 'Retardo'),
        ('EARLY_LEAVE', 'Salida Temprana'),
        ('OTHER', 'Otro'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobada'),
        ('REJECTED', 'Rechazada'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='incidents')
    date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_notes = models.TextField(blank=True, null=True, help_text="Notas del administrador")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee} - {self.get_type_display()} ({self.date})"

class LeaveRequest(models.Model):
    """Modelo para solicitudes de permisos"""
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('APPROVED', 'Aprobada'),
        ('REJECTED', 'Rechazada'),
    )
    
    TYPE_CHOICES = (
        ('VACATION', 'Vacaciones'),
        ('PERSONAL', 'Día Personal'),
        ('SICK', 'Enfermedad'),
        ('OTHER', 'Otro'),
    )
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='VACATION')
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_notes = models.TextField(blank=True, null=True, help_text="Notas del administrador")
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.employee} - {self.get_type_display()} ({self.start_date} - {self.end_date})"
    
    @property
    def days_requested(self):
        """Calcula los días solicitados"""
        return (self.end_date - self.start_date).days + 1
