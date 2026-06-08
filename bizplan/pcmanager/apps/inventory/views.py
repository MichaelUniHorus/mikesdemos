from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from .models import Component, ComponentCategory, AssembledPC, ActionLog
from .forms import ComponentForm, AssembledPCForm

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
def component_list(request):
    category_slug = request.GET.get('category')
    components = Component.objects.all()
    
    if category_slug:
        category = get_object_or_404(ComponentCategory, slug=category_slug)
        components = components.filter(category=category)
    
    categories = ComponentCategory.objects.all()
    
    # Pagination
    paginator = Paginator(components, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
    }
    return render(request, 'inventory/list.html', context)

@login_required
def component_add(request):
    entry_type = request.GET.get('type', 'component')
    
    if entry_type == 'assembled':
        if request.method == 'POST':
            form = AssembledPCForm(request.POST)
            if form.is_valid():
                pc = form.save(commit=False)
                # Списать комплектующие со склада
                for field in ['cpu', 'gpu', 'ram', 'ssd', 'cooler', 'case', 'psu', 'motherboard']:
                    comp = getattr(pc, field)
                    if comp and comp.quantity > 0:
                        comp.quantity -= 1
                        comp.save()
                pc.save()
                log_action(request.user, 'create', 'AssembledPC', pc, f'Добавлен готовый ПК: {pc.title}')
                return redirect('assembled_pc_list')
        else:
            form = AssembledPCForm()
        return render(request, 'inventory/assembled_form.html', {'form': form, 'title': 'Добавить готовый ПК на склад'})
    
    else:
        if request.method == 'POST':
            form = ComponentForm(request.POST)
            if form.is_valid():
                component = form.save()
                log_action(request.user, 'create', 'Component', component, f'Добавлено: {component.name}')
                return redirect('component_list')
        else:
            form = ComponentForm()
        
        return render(request, 'inventory/form.html', {'form': form, 'title': 'Добавить комплектующее', 'entry_type': entry_type})

@login_required
def component_edit(request, pk):
    component = get_object_or_404(Component, pk=pk)
    
    if request.method == 'POST':
        form = ComponentForm(request.POST, instance=component)
        if form.is_valid():
            form.save()
            log_action(request.user, 'update', 'Component', component, f'Обновлено: {component.name}')
            return redirect('component_list')
    else:
        form = ComponentForm(instance=component)
    
    return render(request, 'inventory/form.html', {'form': form, 'title': 'Редактировать комплектующее'})

@login_required
def component_delete(request, pk):
    component = get_object_or_404(Component, pk=pk)
    name = component.name
    component.delete()
    log_action(request.user, 'delete', 'Component', None, f'Удалено: {name}')
    messages.success(request, f'Комплектующее "{name}" удалено')
    return redirect('component_list')

@login_required
def assembled_pc_list(request):
    pcs = AssembledPC.objects.all()
    context = {'pcs': pcs}
    return render(request, 'inventory/assembled_list.html', context)

@login_required
def assembled_pc_add(request):
    if request.method == 'POST':
        form = AssembledPCForm(request.POST)
        if form.is_valid():
            pc = form.save()
            log_action(request.user, 'create', 'AssembledPC', pc, f'Добавлен готовый ПК: {pc.title}')
            return redirect('assembled_pc_list')
    else:
        form = AssembledPCForm()
    
    return render(request, 'inventory/assembled_form.html', {'form': form, 'title': 'Добавить готовый ПК на склад'})

@login_required
def assembled_pc_detail(request, pk):
    pc = get_object_or_404(AssembledPC, pk=pk)
    return render(request, 'inventory/assembled_detail.html', {'pc': pc})

@login_required
def assembled_pc_disassemble(request, pk):
    pc = get_object_or_404(AssembledPC, pk=pk)
    title = pc.title
    pc.disassemble()
    log_action(request.user, 'disassemble', 'AssembledPC', None, f'Разобран ПК: {title}')
    messages.success(request, f'ПК "{title}" разобран, комплектующие возвращены на склад')
    return redirect('assembled_pc_list')
