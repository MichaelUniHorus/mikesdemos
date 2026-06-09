from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from apps.inventory.models import Component, ComponentCategory
from apps.builds.models import PCBuild

def get_date_range(period, start_date=None, end_date=None):
    today = datetime.now()
    if period == 'month':
        start = today.replace(day=1)
        end = today
    elif period == 'quarter':
        quarter = (today.month - 1) // 3
        start = today.replace(month=quarter * 3 + 1, day=1)
        end = today
    elif period == 'year':
        start = today.replace(month=1, day=1)
        end = today
    elif period == 'custom' and start_date and end_date:
        return datetime.strptime(start_date, '%Y-%m-%d'), datetime.strptime(end_date, '%Y-%m-%d')
    else:
        start = today.replace(month=1, day=1)
        end = today
    return start, end

@login_required
def dashboard_view(request):
    period = request.GET.get('period', 'month')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    start, end = get_date_range(period, start_date, end_date)

    # Статистика по ПК за период
    builds_in_period = PCBuild.objects.filter(sold_at_timestamp__gte=start, sold_at_timestamp__lte=end)
    total_sold = builds_in_period.count()
    total_sales = builds_in_period.aggregate(total=models.Sum('sale_price'))['total'] or 0
    total_profit = sum(b.profit or 0 for b in builds_in_period)

    # Время сборки/продажи
    sold_builds = builds_in_period.filter(status='sold')
    avg_assembly_time = sum(b.assembly_time_days or 0 for b in sold_builds) / max(sold_builds.count(), 1)
    avg_sale_time = sum(b.sale_time_days or 0 for b in sold_builds) / max(sold_builds.count(), 1)

    # Графики по месяцам
    monthly_data = builds_in_period.annotate(month=TruncMonth('sold_at_timestamp')).values('month').annotate(
        count=models.Count('id'),
        revenue=models.Sum('sale_price')
    ).order_by('month')

    # Статистика по складу
    total_inventory_value = Component.objects.aggregate(
        total=models.Sum(models.F('purchase_price') * models.F('quantity'))
    )['total'] or 0

    categories = ComponentCategory.objects.all()
    category_stats = []
    for cat in categories:
        comps = cat.components.all()
        total_qty = sum(c.quantity for c in comps)
        total_val = sum(c.total_value for c in comps)
        used_qty = sum(c.used_quantity for c in comps)
        category_stats.append({
            'name': cat.name,
            'quantity': total_qty,
            'used': used_qty,
            'available': total_qty - used_qty,
            'value': total_val,
        })

    recent_sales = PCBuild.objects.filter(status='sold').order_by('-sold_at')[:5]

    context = {
        'period': period,
        'start_date': start.strftime('%Y-%m-%d'),
        'end_date': end.strftime('%Y-%m-%d'),
        'total_sold': total_sold,
        'total_sales': total_sales,
        'total_profit': total_profit,
        'total_inventory_value': total_inventory_value,
        'category_stats': category_stats,
        'recent_sales': recent_sales,
        'avg_assembly_time': round(avg_assembly_time, 1),
        'avg_sale_time': round(avg_sale_time, 1),
        'monthly_data': list(monthly_data),
    }
    return render(request, 'dashboard/index.html', context)
