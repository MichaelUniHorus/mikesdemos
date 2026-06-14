from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncWeek
from datetime import datetime, timedelta
from .models import FinanceOperation, DocumentCategory, Document
from .forms import FinanceOperationForm

@login_required
def finance_index(request):
    """Главная страница финансов"""
    return redirect('finance_operations')

@login_required
def finance_operations(request):
    """Список операций с фильтрами"""
    operations = FinanceOperation.objects.all()
    
    # Фильтры
    op_type = request.GET.get('type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    search = request.GET.get('search')
    
    if op_type:
        operations = operations.filter(operation_type=op_type)
    if date_from:
        operations = operations.filter(date__gte=date_from)
    if date_to:
        operations = operations.filter(date__lte=date_to)
    if search:
        operations = operations.filter(name__icontains=search) | operations.filter(payment_purpose__icontains=search)
    
    # Итоги
    total_income = operations.filter(operation_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = operations.filter(operation_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense
    
    context = {
        'operations': operations,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
        'filter_type': op_type,
        'filter_date_from': date_from,
        'filter_date_to': date_to,
        'filter_search': search,
    }
    return render(request, 'finance/operations.html', context)

@login_required
def finance_operation_add(request):
    """Добавить операцию"""
    if request.method == 'POST':
        form = FinanceOperationForm(request.POST)
        if form.is_valid():
            op = form.save(commit=False)
            op.created_by = request.user
            op.save()
            messages.success(request, 'Операция добавлена')
            return redirect('finance_operations')
    else:
        form = FinanceOperationForm()
    
    return render(request, 'finance/operation_form.html', {'form': form, 'title': 'Добавить операцию'})

@login_required
def finance_operation_delete(request, pk):
    """Удалить операцию"""
    op = get_object_or_404(FinanceOperation, pk=pk)
    op.delete()
    messages.success(request, 'Операция удалена')
    return redirect('finance_operations')

@login_required
def finance_statistics(request):
    """Статистика по финансам"""
    from apps.builds.models import PCBuild
    
    # По месяцам за текущий год
    year = datetime.now().year
    monthly_stats = FinanceOperation.objects.filter(date__year=year).annotate(
        month=TruncMonth('date')
    ).values('month', 'operation_type').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # По неделям за текущий месяц
    now = datetime.now()
    week_start = now - timedelta(days=now.weekday())
    weekly_stats = FinanceOperation.objects.filter(date__gte=week_start).annotate(
        week=TruncWeek('date')
    ).values('week', 'operation_type').annotate(
        total=Sum('amount')
    ).order_by('week')
    
    # Сводка за год
    year_income = FinanceOperation.objects.filter(date__year=year, operation_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    year_expense = FinanceOperation.objects.filter(date__year=year, operation_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Данные для круговой диаграммы по категориям (назначения платежей)
    expense_by_purpose = FinanceOperation.objects.filter(
        date__year=year, 
        operation_type='expense'
    ).values('payment_purpose').annotate(total=Sum('amount')).order_by('-total')[:10]
    
    # Маржинальность проданных ПК
    sold_builds = PCBuild.objects.filter(status='sold', sold_at_timestamp__year=year)
    profit_by_build = []
    for build in sold_builds:
        if build.profit:
            profit_by_build.append({
                'title': build.title,
                'cost_price': build.cost_price,
                'sale_price': build.sale_price,
                'profit': build.profit,
                'margin': (build.profit / build.sale_price * 100) if build.sale_price else 0,
                'sold_at': build.sold_at_timestamp,
            })
    
    context = {
        'monthly_stats': list(monthly_stats),
        'weekly_stats': list(weekly_stats),
        'year_income': year_income,
        'year_expense': year_expense,
        'year_balance': year_income - year_expense,
        'expense_by_purpose': list(expense_by_purpose),
        'profit_by_build': profit_by_build,
        'current_year': year,
    }
    return render(request, 'finance/statistics.html', context)

@login_required
def documents_index(request):
    """Список категорий документов"""
    categories = DocumentCategory.objects.all()
    return render(request, 'finance/documents.html', {'categories': categories})

@login_required
def documents_category(request, slug):
    """Документы категории"""
    category = get_object_or_404(DocumentCategory, slug=slug)
    documents = category.documents.all()
    return render(request, 'finance/documents_category.html', {'category': category, 'documents': documents})

@login_required
def document_upload(request, category_slug):
    """Загрузить документ"""
    category = get_object_or_404(DocumentCategory, slug=category_slug)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        file = request.FILES.get('file')
        if title and file:
            Document.objects.create(
                title=title,
                category=category,
                file=file,
                description=description,
                uploaded_by=request.user
            )
            messages.success(request, 'Документ загружен')
            return redirect('documents_category', slug=category_slug)
    return render(request, 'finance/document_form.html', {'category': category, 'title': 'Загрузить документ'})

@login_required
def document_delete(request, pk):
    """Удалить документ"""
    doc = get_object_or_404(Document, pk=pk)
    slug = doc.category.slug
    doc.file.delete()
    doc.delete()
    messages.success(request, 'Документ удален')
    return redirect('documents_category', slug=slug)
