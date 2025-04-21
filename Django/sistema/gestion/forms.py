from django import forms
from .models import Gasto

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['descripcion',
                  'monto',
                  'fecha_limite',
                  'tipo_gasto',
                ]
        widgets = {
            'fecha_limite': forms.DateInput(attrs={'type': 'date'}),
            'tipo_gasto' : forms.Select(attrs={'class': 'form-control'}),
        }