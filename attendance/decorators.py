from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def login_required(view_func):
    """Decorador que requiere que el usuario esté autenticado"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('employee_id'):
            return redirect('/login')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    """Decorador que requiere que el usuario sea admin"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        employee_id = request.session.get('employee_id')
        employee_role = request.session.get('employee_role')
        
        if not employee_id:
            return redirect('/login')
        
        if employee_role != 'ADMIN':
            return HttpResponseForbidden('Acceso denegado. Solo administradores.')
        
        return view_func(request, *args, **kwargs)
    return wrapper

def employee_required(view_func):
    """Decorador que requiere que el usuario sea empleado"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        employee_id = request.session.get('employee_id')
        employee_role = request.session.get('employee_role')
        
        if not employee_id:
            return redirect('/login')
        
        if employee_role != 'EMPLOYEE':
            return HttpResponseForbidden('Acceso denegado. Solo empleados.')
        
        return view_func(request, *args, **kwargs)
    return wrapper
