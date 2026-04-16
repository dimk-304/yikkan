from django.urls import path
from .views import (
    EmployeeRegistrationView, 
    EmployeeFaceRegistrationView,
    AttendanceCheckView, 
    RecentLogsView,
    EmployeeListView,
    EmployeeDetailView,
    AttendanceLogsView,
    StatsView,
    ExportLogsView,
)
from .auth_views import (
    LoginView,
    LogoutView,
    CurrentUserView,
    IncidentListCreateView,
    AdminIncidentListView,
    AdminIncidentUpdateView,
    LeaveRequestListCreateView,
    AdminLeaveRequestListView,
    AdminLeaveRequestUpdateView,
)
from .employee_views import (
    EmployeeManagementListView,
    EmployeeCreateView,
    EmployeeUpdateView,
    EmployeeDeleteView,
    EmployeeHierarchyTreeView,
    EmployeeSubordinatesView,
    EmployeeSetPasswordView,
    EmployeeSupervisorOptionsView,
    EmployeeDepartmentsView,
)

urlpatterns = [
    # API endpoints originales
    path('register/', EmployeeRegistrationView.as_view(), name='employee-register'),
    path('employees/<int:pk>/register-face/', EmployeeFaceRegistrationView.as_view(), name='employee-register-face'),
    path('check/', AttendanceCheckView.as_view(), name='attendance-check'),
    path('logs/recent/', RecentLogsView.as_view(), name='recent-logs'),
    
    # Endpoints para dashboard
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('logs/', AttendanceLogsView.as_view(), name='logs-list'),
    path('logs/export/', ExportLogsView.as_view(), name='logs-export'),
    path('stats/', StatsView.as_view(), name='stats'),
    
    # Autenticación
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('me/', CurrentUserView.as_view(), name='current-user'),
    
    # Incidencias (empleado)
    path('incidents/', IncidentListCreateView.as_view(), name='incidents'),
    
    # Incidencias (admin)
    path('admin/incidents/', AdminIncidentListView.as_view(), name='admin-incidents'),
    path('admin/incidents/<int:pk>/', AdminIncidentUpdateView.as_view(), name='admin-incident-update'),
    
    # Permisos (empleado)
    path('leave-requests/', LeaveRequestListCreateView.as_view(), name='leave-requests'),
    
    # Permisos (admin)
    path('admin/leave-requests/', AdminLeaveRequestListView.as_view(), name='admin-leave-requests'),
    path('admin/leave-requests/<int:pk>/', AdminLeaveRequestUpdateView.as_view(), name='admin-leave-request-update'),
    
    # Gestión de empleados con jerarquía
    path('employees/management/', EmployeeManagementListView.as_view(), name='employee-management-list'),
    path('employees/create/', EmployeeCreateView.as_view(), name='employee-create'),
    path('employees/<int:pk>/update/', EmployeeUpdateView.as_view(), name='employee-update'),
    path('employees/<int:pk>/delete/', EmployeeDeleteView.as_view(), name='employee-delete'),
    path('employees/<int:pk>/detail/', EmployeeDetailView.as_view(), name='employee-detail-hierarchy'),
    path('employees/hierarchy/', EmployeeHierarchyTreeView.as_view(), name='employee-hierarchy-tree'),
    path('employees/<int:pk>/subordinates/', EmployeeSubordinatesView.as_view(), name='employee-subordinates'),
    path('employees/<int:pk>/set-password/', EmployeeSetPasswordView.as_view(), name='employee-set-password'),
    path('employees/supervisor-options/', EmployeeSupervisorOptionsView.as_view(), name='employee-supervisor-options'),
    path('employees/departments/', EmployeeDepartmentsView.as_view(), name='employee-departments'),
]
