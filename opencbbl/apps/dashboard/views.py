from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from apps.inventory.models import Component, ComponentCategory
from apps.builds.models import PCBuild

@login_required
def dashboard_view(request):
    # Статистика по ПК
    builds_by_status = PCBuild.objects.values('status').count()
    total_sold = PCBuild.objects.filter(status='sold').count()
    total_sales = PCBuild.objects.filter(status='sold').aggregate(
        total=models.Sum('sale_price')
    )['total'] or 0
    
    # Статистика по складу
    total_inventory_value = Component.objects.aggregate(
        total=models.Sum(models.F('purchase_price') * models.F('quantity'))
    )['total'] or 0
    
    # Остатки по категориям
    categories = ComponentCategory.objects.all()
    category_stats = []
    for cat in categories:
        comps = cat.components.all()
        total_qty = sum(c.quantity for c in comps)
        total_val = sum(c.total_value for c in comps)
        category_stats.append({
            'name': cat.name,
            'quantity': total_qty,
            'value': total_val,
        })
    
    # Последние продажи
    recent_sales = PCBuild.objects.filter(status='sold').order_by('-sold_at')[:5]
    
    context = {
        'builds_by_status': builds_by_status,
        'total_sold': total_sold,
        'total_sales': total_sales,
        'total_inventory_value': total_inventory_value,
        'category_stats': category_stats,
        'recent_sales': recent_sales,
    }
    return render(request, 'dashboard/index.html', context)
