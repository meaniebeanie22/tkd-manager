from django.forms import ModelForm
from django.forms.widgets import DateInput, TimeInput
from .models import GradingResult, Class

class GradingResultForm(ModelForm):
    class Meta:
        model = GradingResult
        fields = ['member','date','type','forbelt','assessor','comments','award']

class ClassForm(ModelForm):
    class Meta:
        model = Class
        fields = ['type','date','start','end','instructors','students']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
            'start': TimeInput(attrs={'type': 'time'}),
            'end': TimeInput(attrs={'type': 'time'}),
        }
