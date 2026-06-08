from django.db import models
from django.utils import timezone


class Region(models.Model):
    okato = models.IntegerField(unique=True, verbose_name='Код ОКАТО')
    name_ru = models.CharField(max_length=200, verbose_name='Название (рус.)')
    name_en = models.CharField(max_length=200, blank=True, null=True, verbose_name='Название (англ.)')
    
    class Meta:
        verbose_name = 'Субъект РФ'
        verbose_name_plural = 'Субъекты РФ'
        ordering = ['name_ru']
    
    def __str__(self):
        return self.name_ru


class Thema(models.Model):
    thema_id = models.IntegerField(unique=True, verbose_name='ID признака')
    name_ru = models.CharField(max_length=500, verbose_name='Наименование (рус.)')
    name_en = models.CharField(max_length=500, blank=True, null=True, verbose_name='Наименование (англ.)')
    
    class Meta:
        verbose_name = 'Признак нелегальной деятельности'
        verbose_name_plural = 'Признаки нелегальной деятельности'
        ordering = ['name_ru']
    
    def __str__(self):
        return self.name_ru


class Organization(models.Model):
    cbr_id = models.IntegerField(unique=True, verbose_name='ID в ЦБ РФ')
    name = models.TextField(blank=True, null=True, verbose_name='Название организации', db_index=False)
    inn = models.CharField(max_length=12, blank=True, null=True, verbose_name='ИНН')
    address = models.TextField(blank=True, null=True, verbose_name='Адрес')
    website = models.TextField(blank=True, null=True, verbose_name='Сайты')
    sign = models.TextField(blank=True, null=True, verbose_name='Признак нелегальной деятельности')
    is_closed = models.BooleanField(default=False, verbose_name='Закрыта')
    comment = models.TextField(blank=True, null=True, verbose_name='Комментарий')
    cbr_date_added = models.DateField(blank=True, null=True, verbose_name='Дата внесения')
    cbr_date_updated = models.DateTimeField(blank=True, null=True, verbose_name='Дата обновления')
    org_type = models.CharField(max_length=200, blank=True, null=True, verbose_name='Тип организации')
    
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Субъект РФ')
    thema = models.ForeignKey(Thema, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Признак нелегальной деятельности')
    
    latitude = models.FloatField(blank=True, null=True, verbose_name='Широта')
    longitude = models.FloatField(blank=True, null=True, verbose_name='Долгота')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        ordering = ['-cbr_date_added']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['inn']),
            models.Index(fields=['region']),
            models.Index(fields=['thema']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.inn or 'без ИНН'})"


class Location(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='locations', verbose_name='Организация')
    address = models.TextField(verbose_name='Адрес')
    latitude = models.FloatField(blank=True, null=True, verbose_name='Широта')
    longitude = models.FloatField(blank=True, null=True, verbose_name='Долгота')
    is_geocoded = models.BooleanField(default=False, verbose_name='Координаты получены')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.address[:50]}..."
