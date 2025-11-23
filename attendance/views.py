from rest_framework import views, status, parsers, generics
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Employee, AttendanceLog
from .serializers import (
    EmployeeSerializer, EmployeeDetailSerializer, EmployeeListSerializer,
    AttendanceLogSerializer, AttendanceLogDetailSerializer
)
from .utils import get_face_encoding, compare_faces
from .decorators import login_required, admin_required, employee_required
import csv
from django.http import HttpResponse

class EmployeeRegistrationView(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def post(self, request):
        serializer = EmployeeSerializer(data=request.data)
        if serializer.is_valid():
            photo = request.FILES.get('photo')
            if not photo:
                return Response({'error': 'Photo is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Generar encoding
            encoding = get_face_encoding(photo)
            if encoding is None:
                return Response({'error': 'No face detected in the photo'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Guardar empleado con encoding
            employee = serializer.save(face_encoding=encoding)
            return Response(EmployeeSerializer(employee).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AttendanceCheckView(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def post(self, request):
        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': 'Photo is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generar encoding de la foto recibida
        unknown_encoding = get_face_encoding(photo)
        if unknown_encoding is None:
            return Response({'error': 'No face detected'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener todos los empleados activos con encodings
        employees = Employee.objects.filter(is_active=True).exclude(face_encoding__isnull=True)
        known_encodings = [e.face_encoding for e in employees]
        
        if not known_encodings:
            return Response({'error': 'No registered employees to match against'}, status=status.HTTP_404_NOT_FOUND)

        # Comparar
        match_index = compare_faces(known_encodings, unknown_encoding)
        
        if match_index != -1:
            matched_employee = employees[match_index]
            
            # Determinar tipo de registro (Entrada/Salida)
            last_log = AttendanceLog.objects.filter(employee=matched_employee).order_by('-timestamp').first()
            log_type = 'CHECK_IN'
            if last_log and last_log.type == 'CHECK_IN':
                log_type = 'CHECK_OUT'
            
            log = AttendanceLog.objects.create(employee=matched_employee, type=log_type)
            
            return Response({
                'message': f'Attendance recorded: {log_type}',
                'employee': EmployeeSerializer(matched_employee).data,
                'log': AttendanceLogSerializer(log).data
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Face not recognized'}, status=status.HTTP_401_UNAUTHORIZED)

# Vista para obtener registros recientes
class RecentLogsView(views.APIView):
    def get(self, request):
        logs = AttendanceLog.objects.select_related('employee').order_by('-timestamp')[:10]
        return Response(AttendanceLogSerializer(logs, many=True).data)

# NUEVAS VISTAS PARA DASHBOARD

class EmployeeListView(generics.ListAPIView):
    """Lista todos los empleados con opción de búsqueda"""
    serializer_class = EmployeeListSerializer
    
    def get_queryset(self):
        queryset = Employee.objects.all()
        search = self.request.query_params.get('search', None)
        active_only = self.request.query_params.get('active_only', None)
        
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(employee_id__icontains=search) |
                Q(email__icontains=search)
            )
        
        if active_only == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset.order_by('-created_at')

class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Obtener, actualizar o eliminar un empleado"""
    queryset = Employee.objects.all()
    serializer_class = EmployeeDetailSerializer

class AttendanceLogsView(generics.ListAPIView):
    """Lista logs con filtros"""
    serializer_class = AttendanceLogDetailSerializer
    
    def get_queryset(self):
        queryset = AttendanceLog.objects.select_related('employee').all()
        
        # Filtros
        employee_id = self.request.query_params.get('employee_id', None)
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        log_type = self.request.query_params.get('type', None)
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            queryset = queryset.filter(timestamp__gte=start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59)
            queryset = queryset.filter(timestamp__lte=end)
        
        if log_type:
            queryset = queryset.filter(type=log_type)
        
        return queryset.order_by('-timestamp')

class StatsView(views.APIView):
    """Estadísticas generales del sistema"""
    def get(self, request):
        today = timezone.now().date()
        
        stats = {
            'total_employees': Employee.objects.filter(is_active=True).count(),
            'total_logs_today': AttendanceLog.objects.filter(
                timestamp__date=today
            ).count(),
            'employees_checked_in_today': AttendanceLog.objects.filter(
                timestamp__date=today,
                type='CHECK_IN'
            ).values('employee').distinct().count(),
            'total_logs': AttendanceLog.objects.count(),
        }
        
        return Response(stats)

class ExportLogsView(views.APIView):
    """Exportar logs a CSV"""
    def get(self, request):
        # Obtener parámetros de filtro
        employee_id = request.query_params.get('employee_id', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        
        queryset = AttendanceLog.objects.select_related('employee').all()
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            queryset = queryset.filter(timestamp__gte=start)
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            end = end.replace(hour=23, minute=59, second=59)
            queryset = queryset.filter(timestamp__lte=end)
        
        queryset = queryset.order_by('-timestamp')
        
        # Crear CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="attendance_logs.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Empleado', 'ID Empleado', 'Tipo', 'Fecha y Hora'])
        
        for log in queryset:
            writer.writerow([
                log.id,
                f"{log.employee.first_name} {log.employee.last_name}",
                log.employee.employee_id,
                'Entrada' if log.type == 'CHECK_IN' else 'Salida',
                log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response

# Vistas para templates - CON PROTECCIÓN
@login_required
def index_view(request):
    # Redirigir según rol
    role = request.session.get('employee_role')
    if role == 'ADMIN':
        return redirect('/dashboard')
    elif role == 'EMPLOYEE':
        return redirect('/employee-panel')
    return render(request, 'index.html')

@admin_required
def register_view(request):
    return render(request, 'register.html')

# attendance_view SIN protección (libre)
def attendance_view(request):
    return render(request, 'attendance.html')

@admin_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

@admin_required
def employees_view(request):
    return render(request, 'employees.html')

@admin_required
def history_view(request):
    return render(request, 'history.html')

@admin_required
def employees_management_view(request):
    return render(request, 'employees_management.html')

