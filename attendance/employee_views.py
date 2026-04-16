from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Employee
from .serializers import (
    EmployeeHierarchySerializer,
    EmployeeCreateUpdateSerializer,
    EmployeePasswordSerializer,
    SubordinateSerializer
)
from .decorators import employee_required

class EmployeeManagementListView(generics.ListAPIView):
    """Lista todos los empleados con información de jerarquía"""
    serializer_class = EmployeeHierarchySerializer
    
    def get_queryset(self):
        queryset = Employee.objects.all().select_related('supervisor')
        
        # Filtros
        role = self.request.query_params.get('role', None)
        department = self.request.query_params.get('department', None)
        supervisor_id = self.request.query_params.get('supervisor', None)
        search = self.request.query_params.get('search', None)
        is_active = self.request.query_params.get('is_active', None)
        
        if role:
            queryset = queryset.filter(role=role)
        
        if department:
            queryset = queryset.filter(department__icontains=department)
        
        if supervisor_id:
            queryset = queryset.filter(supervisor_id=supervisor_id)
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(employee_id__icontains=search)
            )
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('role', 'last_name', 'first_name')

class EmployeeCreateView(generics.CreateAPIView):
    """Crear nuevo empleado"""
    queryset = Employee.objects.all()
    serializer_class = EmployeeCreateUpdateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        
        # Retornar con el serializer de jerarquía para tener toda la info
        response_serializer = EmployeeHierarchySerializer(employee)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class EmployeeUpdateView(generics.UpdateAPIView):
    """Actualizar empleado existente"""
    queryset = Employee.objects.all()
    serializer_class = EmployeeCreateUpdateSerializer
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        employee = serializer.save()
        
        # Retornar con el serializer de jerarquía
        response_serializer = EmployeeHierarchySerializer(employee)
        return Response(response_serializer.data)

class EmployeeDeleteView(generics.DestroyAPIView):
    """Desactivar empleado (soft delete)"""
    queryset = Employee.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(
            {'message': 'Empleado desactivado exitosamente'},
            status=status.HTTP_200_OK
        )

class EmployeeDetailView(generics.RetrieveAPIView):
    """Obtener detalles de un empleado"""
    queryset = Employee.objects.all()
    serializer_class = EmployeeHierarchySerializer

class EmployeeHierarchyTreeView(APIView):
    """Obtener el árbol jerárquico completo de la organización"""
    
    def get(self, request):
        # Obtener todos los CEOs (empleados sin supervisor o con rol CEO)
        ceos = Employee.objects.filter(
            Q(role='CEO') | Q(supervisor__isnull=True, role__in=['CEO', 'DIRECTOR', 'MANAGER'])
        ).filter(is_active=True)
        
        def build_tree(employee):
            """Construye recursivamente el árbol de subordinados"""
            subordinates = employee.get_subordinates()
            return {
                'id': employee.id,
                'name': f"{employee.first_name} {employee.last_name}",
                'role': employee.role,
                'role_display': employee.get_role_display(),
                'department': employee.department,
                'position': employee.position,
                'employee_id': employee.employee_id,
                'subordinates': [build_tree(sub) for sub in subordinates]
            }
        
        tree = [build_tree(ceo) for ceo in ceos]
        return Response(tree)

class EmployeeSubordinatesView(generics.ListAPIView):
    """Obtener subordinados directos de un empleado"""
    serializer_class = SubordinateSerializer
    
    def get_queryset(self):
        employee_id = self.kwargs.get('pk')
        try:
            employee = Employee.objects.get(pk=employee_id)
            return employee.get_subordinates()
        except Employee.DoesNotExist:
            return Employee.objects.none()

class EmployeeSetPasswordView(APIView):
    """Cambiar contraseña de un empleado"""
    
    def post(self, request, pk):
        try:
            employee = Employee.objects.get(pk=pk)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Empleado no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = EmployeePasswordSerializer(data=request.data)
        if serializer.is_valid():
            employee.set_password(serializer.validated_data['new_password'])
            employee.save()
            return Response(
                {'message': 'Contraseña actualizada exitosamente'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmployeeSupervisorOptionsView(APIView):
    """Obtener lista de posibles supervisores según el rol"""
    
    def get(self, request):
        role = request.query_params.get('role', None)
        current_employee_id = request.query_params.get('current_id', None)
        
        if not role:
            return Response(
                {'error': 'Se requiere el parámetro role'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Definir qué roles pueden supervisar a cada rol
        supervisor_roles = {
            'CEO': [],  # CEO no tiene supervisor
            'DIRECTOR': ['CEO'],
            'MANAGER': ['CEO', 'DIRECTOR'],
            'OPERATOR': ['CEO', 'DIRECTOR', 'MANAGER'],
            'EMPLOYEE': ['CEO', 'DIRECTOR', 'MANAGER'],
            'ADMIN': ['CEO', 'DIRECTOR'],
        }
        
        allowed_roles = supervisor_roles.get(role, [])
        
        if not allowed_roles:
            return Response([])
        
        # Obtener empleados con esos roles
        queryset = Employee.objects.filter(is_active=True).filter(
            Q(role__in=allowed_roles) | Q(is_superadmin=True)
        )
        
        # Excluir al empleado actual si se está editando
        if current_employee_id:
            queryset = queryset.exclude(id=current_employee_id)
        
        # Serializar
        supervisors = [{
            'id': emp.id,
            'name': f"{emp.first_name} {emp.last_name}",
            'role': emp.role,
            'role_display': emp.get_role_display(),
            'department': emp.department
        } for emp in queryset]
        
        return Response(supervisors)

class EmployeeDepartmentsView(APIView):
    """Obtener lista de departamentos únicos"""
    
    def get(self, request):
        departments = Employee.objects.filter(
            department__isnull=False,
            is_active=True
        ).values_list('department', flat=True).distinct().order_by('department')
        
        return Response(list(departments))
