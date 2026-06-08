from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import PCBuild
from .forms import PCBuildForm
from apps.inventory.models import ActionLog

def log_action(user, action, model_name, obj, description=''):
    ActionLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=obj.pk if obj else None,
        object_name=str(obj) if obj else '',
        description=description
    )

@login_required
def kanban_view(request):
    builds = PCBuild.objects.all()
    assembling = builds.filter(status='assembling')
    for_sale = builds.filter(status='for_sale')
    sold = builds.filter(status='sold')
    
    context = {
        'assembling': assembling,
        'for_sale': for_sale,
        'sold': sold,
    }
    return render(request, 'builds/kanban.html', context)

@login_required
def build_add(request):
    if request.method == 'POST':
        form = PCBuildForm(request.POST)
        if form.is_valid():
            build = form.save(commit=False)
            build.created_by = request.user
            build.save()
            log_action(request.user, 'create', 'PCBuild', build, f'Создана сборка: {build.title}')
            return redirect('kanban')
    else:
        form = PCBuildForm()
    
    return render(request, 'builds/form.html', {'form': form, 'title': 'Новая сборка'})

@login_required
def build_detail(request, pk):
    build = get_object_or_404(PCBuild, pk=pk)
    return render(request, 'builds/detail.html', {'build': build})

@login_required
def build_edit(request, pk):
    build = get_object_or_404(PCBuild, pk=pk)
    
    if request.method == 'POST':
        form = PCBuildForm(request.POST, instance=build)
        if form.is_valid():
            form.save()
            log_action(request.user, 'update', 'PCBuild', build, f'Обновлена сборка: {build.title}')
            return redirect('build_detail', pk=build.pk)
    else:
        form = PCBuildForm(instance=build)
    
    return render(request, 'builds/form.html', {'form': form, 'title': 'Редактировать сборку'})

@login_required
def build_change_status(request, pk, status):
    build = get_object_or_404(PCBuild, pk=pk)
    
    if status in ['assembling', 'for_sale', 'sold']:
        old_status = build.status
        build.status = status
        if status == 'sold' and not build.sold_at:
            from django.utils import timezone
            build.sold_at = timezone.now()
        build.save()
        log_action(request.user, 'status_change', 'PCBuild', build, f'Статус {build.title}: {old_status} → {status}')
    
    return redirect('kanban')
