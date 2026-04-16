from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from attendance.decorators import login_required
from attendance.models import Employee
from .models import Post
from .forms import PostForm

@login_required
def feed_view(request):
    """Vista del feed de publicaciones"""
    posts = Post.objects.select_related('author').all()
    form = PostForm()
    
    # Obtener el empleado actual
    employee_id = request.session.get('employee_id')
    is_superadmin = request.session.get('is_superadmin', False)
    current_employee = None
    if employee_id:
        try:
            current_employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            pass
    
    return render(request, 'networking/feed.html', {
        'posts': posts,
        'form': form,
        'current_employee': current_employee,
        'is_superadmin': is_superadmin,
    })

@login_required
def create_post(request):
    """Crear una nueva publicación"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # Obtener el empleado desde la sesión
            employee_id = request.session.get('employee_id')
            try:
                employee = Employee.objects.get(id=employee_id)
                post = form.save(commit=False)
                post.author = employee  # Asignar el Employee directamente
                post.save()
                messages.success(request, '¡Publicación creada exitosamente!')
            except Employee.DoesNotExist:
                messages.error(request, 'Error: Usuario no encontrado.')
            return redirect('networking:feed')
        else:
            messages.error(request, 'Error al crear la publicación.')
    return redirect('networking:feed')

@login_required
def delete_post(request, post_id):
    """Eliminar una publicación"""
    post = get_object_or_404(Post, id=post_id)
    
    # Obtener el empleado desde la sesión
    employee_id = request.session.get('employee_id')
    is_superadmin = request.session.get('is_superadmin', False)
    
    try:
        employee = Employee.objects.get(id=employee_id)
        # Solo el autor o un admin puede eliminar
        if post.author == employee or is_superadmin:
            post.delete()
            messages.success(request, 'Publicación eliminada.')
        else:
            messages.error(request, 'No tienes permiso para eliminar esta publicación.')
    except Employee.DoesNotExist:
        messages.error(request, 'Error: Usuario no encontrado.')
    
    return redirect('networking:feed')
