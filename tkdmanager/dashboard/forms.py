from django.forms import ModelForm, ChoiceField, DateField, ModelChoiceField, ModelMultipleChoiceField, TextInput, Form, DateTimeField
from django.forms.widgets import DateInput, TimeInput, DateTimeInput
from .models import GradingResult, Class, Member, Award, Payment, BELT_CHOICES, GRADINGS
from django.utils import timezone

class GradingResultForm(ModelForm):
    class Meta:
        model = GradingResult
        fields = ['member','date','type','forbelt','assessor','comments','award']

class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = ['first_name','last_name','idnumber','address_line_1','address_line_2','address_line_3','date_of_birth','belt','email','phone','team_leader_instructor','active']
        widgets = {
            'phone': TextInput(attrs={'type': 'tel'})
        }

class ClassForm(ModelForm):
    instructors = ModelMultipleChoiceField(queryset=Member.objects.all().exclude(team_leader_instructor__exact=''))

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

class PaymentForm(ModelForm):
    date_created = DateTimeField(disabled=True, initial=timezone.now())

    class Meta:
        model = Payment
        fields = ['member', 'paymenttype', 'date_created', 'date_due', 'date_paid_in_full', 'amount_due', 'amount_paid']
        widgets = {
            'date_due': DateInput(attrs={'type': 'date'}),
            'date_paid_in_full': DateInput(attrs={'type':'date'})
        }
