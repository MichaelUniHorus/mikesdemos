from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class FinanceOperation(models.Model):
    """Финансовая операция (приход/расход)"""
    OPERATION_TYPES = [
        ('income', 'Приход'),
        ('expense', 'Расход'),
    ]

    date = models.DateField(verbose_name='Дата')
    name = models.CharField(max_length=200, verbose_name='Название')
    operation_type = models.CharField(max_length=10, choices=OPERATION_TYPES, verbose_name='Тип операции')
    payment_purpose = models.CharField(max_length=200, verbose_name='Назначение платежа')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Сумма')
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Финансовая операция'
        verbose_name_plural = 'Финансовые операции'
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.name} ({self.get_operation_type_display()}) - {self.amount} ₽"


class DocumentCategory(models.Model):
    """Категория документов"""
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name='Описание')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    class Meta:
        verbose_name = 'Категория документов'
        verbose_name_plural = 'Категории документов'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Document(models.Model):
    """Документ"""
    title = models.CharField(max_length=200, verbose_name='Название')
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='documents/', verbose_name='Файл')
    description = models.TextField(blank=True, verbose_name='Описание')
    
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title
