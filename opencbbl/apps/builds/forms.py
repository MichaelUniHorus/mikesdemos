from django import forms
from .models import PCBuild
from apps.inventory.models import Component, ComponentCategory, AssembledPC

class PCBuildForm(forms.ModelForm):
    class Meta:
        model = PCBuild
        fields = ['title', 'status', 'assembled_pc', 'cpu', 'gpu', 'ram', 'ssd', 'cooler', 'case', 'psu', 'motherboard', 'sale_price', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем компоненты по категориям и quantity > 0
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
        # Фильтруем готовые ПК только с quantity > 0
        self.fields['assembled_pc'].queryset = AssembledPC.objects.filter(quantity__gt=0)
