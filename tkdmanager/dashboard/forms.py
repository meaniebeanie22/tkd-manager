from django.forms import ModelForm, ChoiceField, DateField, ModelChoiceField, TextInput, Form
from django.forms.widgets import DateInput, TimeInput
from .models import GradingResult, Class, Member, Award, BELT_CHOICES, GRADINGS

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

class GradingResultSearchForm(Form):
    BLANK_CHOICE = [('', '---------')]

    type = ChoiceField(choices=BLANK_CHOICE + GRADINGS, required=False)
    date = DateField(required=False, widget=TextInput(attrs={'type': 'date'}))
    assessor = ModelChoiceField(queryset=Member.objects.all(), required=False)
    member = ModelChoiceField(queryset=Member.objects.all(), required=False)
    award = ModelChoiceField(queryset=Award.objects.all(), required=False)
    forbelt = ChoiceField(choices=BLANK_CHOICE + BELT_CHOICES, required=False)