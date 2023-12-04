from django.forms import ModelForm
from .models import GradingResult

class GradingResultForm(ModelForm):
    class Meta:
        model = GradingResult
        fields = ['member','date','type','forbelt','assessor','comments','award']
