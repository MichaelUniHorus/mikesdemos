from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ComponentCategory(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

class Component(models.Model):
    category = models.ForeignKey(ComponentCategory, on_delete=models.CASCADE, related_name='components')
    name = models.CharField(max_length=200)
    specs = models.TextField(blank=True, help_text='Характеристики (частота, объём и т.д.)')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена закупки')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Комплектующее'
        verbose_name_plural = 'Комплектующие'
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def total_value(self):
        return self.purchase_price * self.quantity

    @property
    def used_in_builds(self):
        """В каких сборках используется компонент"""
        from apps.builds.models import PCBuild
        builds = []
        for field in ['cpu', 'gpu', 'ram', 'ssd', 'cooler', 'case', 'psu', 'motherboard']:
            if self.category.slug == field or (field == 'cpu' and self.category.slug == 'cpu') or \
               (field == 'gpu' and self.category.slug == 'gpu') or \
               (field == 'ram' and self.category.slug == 'ram') or \
               (field == 'ssd' and self.category.slug == 'ssd') or \
               (field == 'cooler' and self.category.slug == 'cooler') or \
               (field == 'case' and self.category.slug == 'case') or \
               (field == 'psu' and self.category.slug == 'psu') or \
               (field == 'motherboard' and self.category.slug == 'motherboard'):
                builds.extend(PCBuild.objects.filter(**{field: self}))
        return builds

class AssembledPC(models.Model):
    """Готовый ПК на складе — как отдельный тип комплектующего"""
    title = models.CharField(max_length=200, verbose_name='Название')
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    
    # Комплектующие (FK на Component)
    cpu = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='assembled_pcs_cpu', null=True, blank=True, verbose_name='Процессор')
    gpu = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='assembled_pcs_gpu', null=True, blank=True, verbose_name='Видеокарта')
    ram = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='assembled_pcs_ram', null=True, blank=True, verbose_name='ОЗУ')
    ssd = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='assembled_pcs_ssd', null=True, blank=True, verbose_name='SSD')
    cooler = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='assembled_pcs_cooler', null=True, blank=True, verbose_name='Охлаждение')
    case = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='assembled_pcs_case', null=True, blank=True, verbose_name='Корпус')
    psu = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='assembled_pcs_psu', null=True, blank=True, verbose_name='Блок питания')
    motherboard = models.ForeignKey(Component, on_delete=models.PROTECT, related_name='assembled_pcs_motherboard', null=True, blank=True, verbose_name='Материнская плата')
    
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Цена продажи')
    notes = models.TextField(blank=True, verbose_name='Заметки')
    
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Готовый ПК на складе'
        verbose_name_plural = 'Готовые ПК на складе'
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.title} (склад, кол-во: {self.quantity})"

    @property
    def cost_price(self):
        """Себестоимость = сумма закупочных цен всех комплектующих"""
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
    def total_value(self):
        """Общая стоимость на складе"""
        return self.cost_price * self.quantity

    def disassemble(self):
        """Извлечь все комплектующие обратно на склад"""
        for field in ['cpu', 'gpu', 'ram', 'ssd', 'cooler', 'case', 'psu', 'motherboard']:
            comp = getattr(self, field)
            if comp:
                comp.quantity += 1
                comp.save()
        self.delete()

class ActionLog(models.Model):
    """Лог действий пользователей"""
    ACTION_CHOICES = [
        ('create', 'Создание'),
        ('update', 'Обновление'),
        ('delete', 'Удаление'),
        ('status_change', 'Смена статуса'),
        ('disassemble', 'Разбор ПК'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='action_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_name = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Лог действия'
        verbose_name_plural = 'Логи действий'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_action_display()} {self.model_name} - {self.object_name}"
