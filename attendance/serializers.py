from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Employee, AttendanceLog, Incident, LeaveRequest


def _validate_strong_password(password: str):
    """Valida contraseña con las reglas de seguridad de Django."""
    try:
        validate_password(password)
    except DjangoValidationError as exc:
        raise serializers.ValidationError({'new_password': list(exc.messages)})

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'email', 'employee_id',
            'photo', 'profile_photo', 'created_at', 'role', 'is_superadmin'
        ]
        read_only_fields = ['created_at']

class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Serializer con todos los campos incluyendo horarios"""
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'email', 'employee_id', 
            'photo', 'profile_photo', 'created_at', 'work_start_time', 'work_end_time',
            'lunch_start_time', 'lunch_end_time', 'is_active', 'role', 'username', 'is_superadmin'
        ]
        read_only_fields = ['created_at']

class EmployeeListSerializer(serializers.ModelSerializer):
    """Serializer para listado de empleados"""
    total_logs = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'email', 'employee_id',
            'work_start_time', 'work_end_time', 'is_active', 'total_logs', 'role', 'is_superadmin', 'profile_photo'
        ]
    
    def get_total_logs(self, obj):
        return obj.logs.count()

class AttendanceLogSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()

    class Meta:
        model = AttendanceLog
        fields = ['id', 'employee', 'employee_name', 'timestamp', 'type']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

class AttendanceLogDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para logs con información del empleado"""
    employee_name = serializers.SerializerMethodField()
    employee_id = serializers.SerializerMethodField()
    
    class Meta:
        model = AttendanceLog
        fields = ['id', 'employee', 'employee_name', 'employee_id', 'timestamp', 'type']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"
    
    def get_employee_id(self, obj):
        return obj.employee.employee_id

# Serializers para Incidencias
class IncidentSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Incident
        fields = [
            'id', 'employee', 'employee_name', 'date', 'type', 'type_display',
            'description', 'status', 'status_display', 'admin_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'employee_name']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

# Serializers para Permisos
class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    days_requested = serializers.ReadOnlyField()
    
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_name', 'start_date', 'end_date',
            'type', 'type_display', 'reason', 'status', 'status_display',
            'admin_notes', 'days_requested', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'employee_name', 'days_requested']
    
    def get_employee_name(self, obj):
        return f"{obj.employee.first_name} {obj.employee.last_name}"

# Serializer para Login
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

# Serializers para Jerarquía de Empleados
class EmployeeHierarchySerializer(serializers.ModelSerializer):
    """Serializer con información de jerarquía"""
    supervisor_name = serializers.SerializerMethodField()
    supervisor_id = serializers.IntegerField(source='supervisor.id', read_only=True)
    subordinates_count = serializers.SerializerMethodField()
    hierarchy_level = serializers.SerializerMethodField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'email', 'employee_id',
            'photo', 'profile_photo', 'role', 'role_display', 'supervisor', 'supervisor_name', 
            'supervisor_id', 'department', 'position', 'username',
            'work_start_time', 'work_end_time', 'lunch_start_time', 
            'lunch_end_time', 'is_active', 'is_superadmin', 'created_at', 'subordinates_count',
            'hierarchy_level'
        ]
        read_only_fields = ['created_at', 'subordinates_count', 'hierarchy_level']
    
    def get_supervisor_name(self, obj):
        if obj.supervisor:
            return f"{obj.supervisor.first_name} {obj.supervisor.last_name}"
        return None
    
    def get_subordinates_count(self, obj):
        return obj.get_subordinates().count()
    
    def get_hierarchy_level(self, obj):
        return obj.get_hierarchy_level()

class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar empleados con validaciones"""
    password_raw = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'email', 'employee_id',
            'photo', 'profile_photo', 'role', 'supervisor', 'department', 'position',
            'username', 'password_raw', 'work_start_time', 'work_end_time',
            'lunch_start_time', 'lunch_end_time', 'is_active', 'is_superadmin'
        ]
    
    def validate(self, data):
        """Validaciones de jerarquía"""
        role = data.get('role')
        supervisor = data.get('supervisor')
        
        # CEO no puede tener supervisor
        if role == 'CEO' and supervisor:
            raise serializers.ValidationError({
                'supervisor': 'Un CEO no puede tener supervisor'
            })
        
        # Validar que el supervisor tenga un rol superior
        if supervisor and role:
            employee_level = {'CEO': 0, 'DIRECTOR': 1, 'MANAGER': 2, 'OPERATOR': 3, 'EMPLOYEE': 4, 'ADMIN': -1}
            if employee_level.get(role, 999) <= employee_level.get(supervisor.role, 999):
                if not supervisor.is_system_admin():
                    raise serializers.ValidationError({
                        'supervisor': f'El supervisor debe tener un rol superior. No puede ser {supervisor.get_role_display()}'
                    })
        
        # Validar que no se cree una referencia circular
        if supervisor and self.instance:
            if supervisor == self.instance:
                raise serializers.ValidationError({
                    'supervisor': 'Un empleado no puede ser su propio supervisor'
                })
            # Verificar que el supervisor no esté en la cadena de subordinados
            if self.instance in supervisor.get_all_subordinates():
                raise serializers.ValidationError({
                    'supervisor': 'Esta asignación crearía una referencia circular en la jerarquía'
                })
        
        return data
    
    def create(self, validated_data):
        password_raw = validated_data.pop('password_raw', None)
        employee = Employee.objects.create(**validated_data)
        
        if password_raw:
            _validate_strong_password(password_raw)
            employee.set_password(password_raw)
            employee.save()
        
        return employee
    
    def update(self, instance, validated_data):
        password_raw = validated_data.pop('password_raw', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password_raw:
            _validate_strong_password(password_raw)
            instance.set_password(password_raw)
        
        instance.save()
        return instance

class EmployeePasswordSerializer(serializers.Serializer):
    """Serializer para cambio de contraseña"""
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden'
            })
        _validate_strong_password(data['new_password'])
        return data

class SubordinateSerializer(serializers.ModelSerializer):
    """Serializer simple para subordinados"""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    subordinates_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'email', 'employee_id',
            'role', 'role_display', 'department', 'position', 
            'is_active', 'subordinates_count'
        ]
    
    def get_subordinates_count(self, obj):
        return obj.get_subordinates().count()

