# Views adicionales para autenticación, incidencias y permisos
from rest_framework import views, status, generics
from rest_framework.response import Response
from django.shortcuts import render, redirect
from .models import Employee, Incident, LeaveRequest
from .serializers import (
    LoginSerializer, IncidentSerializer, LeaveRequestSerializer
)
from .decorators import employee_required

# ============ VIEWS PARA TEMPLATES ============

def login_view(request):
    # Si ya está logueado, redirigir según rol
    if request.session.get('employee_id'):
        role = request.session.get('employee_role')
        if role == 'ADMIN':
            return redirect('/dashboard')
        elif role == 'EMPLOYEE':
            return redirect('/employee-panel')
    return render(request, 'login.html')

@employee_required
def employee_panel_view(request):
    return render(request, 'employee_panel.html')

# ============ VIEWS PARA AUTENTICACIÓN ============

class LoginView(views.APIView):
    """Vista para login de usuarios"""
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        try:
            employee = Employee.objects.get(username=username, is_active=True)
            if employee.check_password(password):
                # Guardar en sesión
                request.session['employee_id'] = employee.id
                request.session['employee_role'] = employee.role
                
                return Response({
                    'success': True,
                    'employee': {
                        'id': employee.id,
                        'name': f"{employee.first_name} {employee.last_name}",
                        'role': employee.role,
                        'email': employee.email
                    },
                    'redirect': '/dashboard' if employee.role == 'ADMIN' else '/employee-panel'
                })
            else:
                return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)
        except Employee.DoesNotExist:
            return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

class LogoutView(views.APIView):
    """Vista para logout"""
    def post(self, request):
        request.session.flush()
        return Response({'success': True})

class CurrentUserView(views.APIView):
    """Vista para obtener usuario actual"""
    def get(self, request):
        employee_id = request.session.get('employee_id')
        if not employee_id:
            return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            employee = Employee.objects.get(id=employee_id)
            from .serializers import EmployeeSerializer
            return Response(EmployeeSerializer(employee).data)
        except Employee.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

# ============ VIEWS PARA INCIDENCIAS ============

class IncidentListCreateView(generics.ListCreateAPIView):
    """Lista y crea incidencias del empleado logueado"""
    serializer_class = IncidentSerializer
    
    def get_queryset(self):
        employee_id = self.request.session.get('employee_id')
        if not employee_id:
            return Incident.objects.none()
        return Incident.objects.filter(employee_id=employee_id)
    
    def perform_create(self, serializer):
        employee_id = self.request.session.get('employee_id')
        serializer.save(employee_id=employee_id)

class AdminIncidentListView(generics.ListAPIView):
    """Lista todas las incidencias (solo admin)"""
    serializer_class = IncidentSerializer
    queryset = Incident.objects.all()

class AdminIncidentUpdateView(generics.UpdateAPIView):
    """Actualiza estado de incidencia (solo admin)"""
    serializer_class = IncidentSerializer
    queryset = Incident.objects.all()

# ============ VIEWS PARA PERMISOS ============

class LeaveRequestListCreateView(generics.ListCreateAPIView):
    """Lista y crea permisos del empleado logueado"""
    serializer_class = LeaveRequestSerializer
    
    def get_queryset(self):
        employee_id = self.request.session.get('employee_id')
        if not employee_id:
            return LeaveRequest.objects.none()
        return LeaveRequest.objects.filter(employee_id=employee_id)
    
    def perform_create(self, serializer):
        employee_id = self.request.session.get('employee_id')
        serializer.save(employee_id=employee_id)

class AdminLeaveRequestListView(generics.ListAPIView):
    """Lista todos los permisos (solo admin)"""
    serializer_class = LeaveRequestSerializer
    queryset = LeaveRequest.objects.all()

class AdminLeaveRequestUpdateView(generics.UpdateAPIView):
    """Actualiza estado de permiso (solo admin)"""
    serializer_class = LeaveRequestSerializer
    queryset = LeaveRequest.objects.all()
