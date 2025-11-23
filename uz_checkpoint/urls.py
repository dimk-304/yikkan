"""
URL configuration for uz_checkpoint project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from attendance.views import (
    index_view, register_view, attendance_view,
    dashboard_view, employees_view, history_view, employees_management_view
)
from attendance.auth_views import login_view, employee_panel_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index_view, name='index'),
    path('login', login_view, name='login'),
    path('register', register_view, name='register'),
    path('attendance', attendance_view, name='attendance'),
    path('dashboard', dashboard_view, name='dashboard'),
    path('employees', employees_view, name='employees'),
    path('employees/management', employees_management_view, name='employees-management'),
    path('history', history_view, name='history'),
    path('employee-panel', employee_panel_view, name='employee-panel'),
    path('api/', include('attendance.urls')),
    path('network/', include('networking.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
