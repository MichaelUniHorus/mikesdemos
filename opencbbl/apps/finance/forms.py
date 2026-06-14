from django import forms
from .models import FinanceOperation

class FinanceOperationForm(forms.ModelForm):
    class Meta:
        model = FinanceOperation
        fields = ['date', 'name', 'operation_type', 'payment_purpose', 'amount']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'operation_type': forms.Select(attrs={'class': 'form-control'}),
            'payment_purpose': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
