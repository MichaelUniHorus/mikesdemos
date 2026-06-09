from django.db import models
from django.contrib.auth import get_user_model
from apps.inventory.models import Component

User = get_user_model()

class BuildTask(models.Model):
    """Задачи для сборки ПК"""
    STATUS_CHOICES = [
        ('todo', 'К выполнению'),
        ('in_progress', 'В работе'),
        ('done', 'Готово'),
    ]
    
    TASK_TYPES = [
        ('photo', 'Сфотографировать'),
        ('avito', 'Выложить на Авито'),
        ('clean', 'Почистить'),
        ('test', 'Протестировать'),
        ('install_os', 'Установить ОС'),
        ('install_programs', 'Установить программы'),
        ('other', 'Другое'),
    ]
    
    build = models.ForeignKey('PCBuild', on_delete=models.CASCADE, related_name='tasks')
    task_type = models.CharField(max_length=20, choices=TASK_TYPES, verbose_name='Тип задачи')
    description = models.TextField(blank=True, verbose_name='Описание')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo', verbose_name='Статус')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_task_type_display()} - {self.build.title} ({self.get_status_display()})"

class PCBuild(models.Model):
    STATUS_CHOICES = [
        ('assembling', 'Собирается'),
        ('for_sale', 'На продаже'),
        ('sold', 'Продан'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assembling', verbose_name='Статус')
    
    # Готовый ПК (альтернатива выбору отдельных компонентов)
    assembled_pc = models.ForeignKey('inventory.AssembledPC', on_delete=models.PROTECT, null=True, blank=True, related_name='used_in_builds', verbose_name='Готовый ПК со склада')
    
    # Комплектующие (FK на Component) — используются если не выбран готовый ПК
    cpu = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='builds_cpu', null=True, blank=True, verbose_name='Процессор')
    gpu = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='builds_gpu', null=True, blank=True, verbose_name='Видеокарта')
    ram = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='builds_ram', null=True, blank=True, verbose_name='ОЗУ')
    ssd = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='builds_ssd', null=True, blank=True, verbose_name='SSD')
    cooler = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='builds_cooler', null=True, blank=True, verbose_name='Охлаждение')
    case = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='builds_case', null=True, blank=True, verbose_name='Корпус')
    psu = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='builds_psu', null=True, blank=True, verbose_name='Блок питания')
    motherboard = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='builds_motherboard', null=True, blank=True, verbose_name='Материнская плата')
    
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Цена продажи')
    sold_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата продажи')
    notes = models.TextField(blank=True, verbose_name='Заметки')
    
    # Даты смены статусов
    assembling_started = models.DateTimeField(null=True, blank=True, verbose_name='Начало сборки')
    for_sale_started = models.DateTimeField(null=True, blank=True, verbose_name='Начало продажи')
    sold_at_timestamp = models.DateTimeField(null=True, blank=True, verbose_name='Дата продажи (время)')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='builds')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Сборка ПК'
        verbose_name_plural = 'Сборки ПК'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    @property
    def cost_price(self):
        """Себестоимость: если выбран готовый ПК — его себестоимость, иначе сумма компонентов"""
        if self.assembled_pc:
            return self.assembled_pc.cost_price
        total = 0
        for field in ['cpu', 'gpu', 'ram', 'ssd', 'cooler', 'case', 'psu', 'motherboard']:
            comp = getattr(self, field)
            if comp:
                total += comp.purchase_price
        return total

    @property
    def profit(self):
        """Валовая прибыль"""
        if self.sale_price:
            return self.sale_price - self.cost_price
        return None

    @property
    def assembly_time_days(self):
        """Время сборки в днях"""
        if self.for_sale_started and self.assembling_started:
            return (self.for_sale_started - self.assembling_started).days
        return None

    @property
    def sale_time_days(self):
        """Время продажи в днях"""
        if self.sold_at_timestamp and self.for_sale_started:
            return (self.sold_at_timestamp - self.for_sale_started).days
        return None

    @property
    def total_time_days(self):
        """Общее время от начала до продажи"""
        if self.sold_at_timestamp and self.assembling_started:
            return (self.sold_at_timestamp - self.assembling_started).days
        return None

    @property
    def task_stats(self):
        """Статистика по задачам"""
        tasks = self.tasks.all()
        return {
            'total': tasks.count(),
            'todo': tasks.filter(status='todo').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'done': tasks.filter(status='done').count(),
        }

    def save(self, *args, **kwargs):
        from django.utils import timezone
        if self.pk:
            old = PCBuild.objects.get(pk=self.pk)
            if old.status != self.status:
                if self.status == 'assembling' and not self.assembling_started:
                    self.assembling_started = timezone.now()
                elif self.status == 'for_sale' and not self.for_sale_started:
                    self.for_sale_started = timezone.now()
                elif self.status == 'sold':
                    self.sold_at_timestamp = timezone.now()
                    self._deduct_components()
        super().save(*args, **kwargs)

    def _deduct_components(self):
        """Списать по 1 единице каждого компонента"""
        if self.assembled_pc:
            if self.assembled_pc.quantity > 0:
                self.assembled_pc.quantity -= 1
                self.assembled_pc.save()
        else:
            for field in ['cpu', 'gpu', 'ram', 'ssd', 'cooler', 'case', 'psu', 'motherboard']:
                comp = getattr(self, field)
                if comp and comp.quantity > 0:
                    comp.quantity -= 1
                    comp.save()
