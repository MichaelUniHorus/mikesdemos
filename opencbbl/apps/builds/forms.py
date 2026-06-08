from django import forms
from .models import PCBuild, BuildTask
from apps.inventory.models import Component, ComponentCategory, AssembledPC

class BuildTaskForm(forms.ModelForm):
    class Meta:
        model = BuildTask
        fields = ['task_type', 'description', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

class PCBuildForm(forms.ModelForm):
    # Поля для создания новых компонентов прямо в форме сборки
    new_cpu_name = forms.CharField(required=False, label='Новый процессор', widget=forms.TextInput(attrs={'placeholder': 'Название'}))
    new_cpu_price = forms.DecimalField(required=False, label='Цена CPU', widget=forms.NumberInput(attrs={'placeholder': '0.00'}))
    new_gpu_name = forms.CharField(required=False, label='Новая видеокарта')
    new_gpu_price = forms.DecimalField(required=False, label='Цена GPU')
    new_ram_name = forms.CharField(required=False, label='Новая ОЗУ')
    new_ram_price = forms.DecimalField(required=False, label='Цена ОЗУ')
    new_ssd_name = forms.CharField(required=False, label='Новый SSD')
    new_ssd_price = forms.DecimalField(required=False, label='Цена SSD')
    new_cooler_name = forms.CharField(required=False, label='Новое охлаждение')
    new_cooler_price = forms.DecimalField(required=False, label='Цена охлаждения')
    new_case_name = forms.CharField(required=False, label='Новый корпус')
    new_case_price = forms.DecimalField(required=False, label='Цена корпуса')
    new_psu_name = forms.CharField(required=False, label='Новый БП')
    new_psu_price = forms.DecimalField(required=False, label='Цена БП')
    new_motherboard_name = forms.CharField(required=False, label='Новая материнка')
    new_motherboard_price = forms.DecimalField(required=False, label='Цена материнки')

    class Meta:
        model = PCBuild
        fields = ['title', 'status', 'assembled_pc', 'cpu', 'gpu', 'ram', 'ssd', 'cooler', 'case', 'psu', 'motherboard', 'sale_price', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        category_map = {
            'cpu': 'cpu',
            'gpu': 'gpu',
            'ram': 'ram',
            'ssd': 'ssd',
            'cooler': 'cooler',
            'case': 'case',
            'psu': 'psu',
            'motherboard': 'motherboard',
        }
        for field, slug in category_map.items():
            self.fields[field].queryset = Component.objects.filter(
                category__slug=slug,
                quantity__gt=0
            )
            self.fields[field].empty_label = '-- Выбрать со склада --'
        self.fields['assembled_pc'].queryset = AssembledPC.objects.filter(quantity__gt=0)
        self.fields['assembled_pc'].empty_label = '-- или выбрать готовый ПК --'

    def save(self, commit=True):
        build = super().save(commit=False)
        
        # Создаем новые компоненты если указаны
        component_map = [
            ('cpu', 'new_cpu_name', 'new_cpu_price', 'cpu'),
            ('gpu', 'new_gpu_name', 'new_gpu_price', 'gpu'),
            ('ram', 'new_ram_name', 'new_ram_price', 'ram'),
            ('ssd', 'new_ssd_name', 'new_ssd_price', 'ssd'),
            ('cooler', 'new_cooler_name', 'new_cooler_price', 'cooler'),
            ('case', 'new_case_name', 'new_case_price', 'case'),
            ('psu', 'new_psu_name', 'new_psu_price', 'psu'),
            ('motherboard', 'new_motherboard_name', 'new_motherboard_price', 'motherboard'),
        ]
        
        for field, name_field, price_field, category_slug in component_map:
            if self.cleaned_data.get(name_field) and not self.cleaned_data.get(field):
                name = self.cleaned_data.get(name_field)
                price = self.cleaned_data.get(price_field) or 0
                category, _ = ComponentCategory.objects.get_or_create(
                    slug=category_slug,
                    defaults={'name': category_slug.upper()}
                )
                component = Component.objects.create(
                    category=category,
                    name=name,
                    purchase_price=price,
                    quantity=1
                )
                setattr(build, field, component)
        
        if commit:
            build.save()
        return build
