from django.forms import ModelForm, ChoiceField, DateField, ModelChoiceField, ModelMultipleChoiceField, TextInput, Form, DateTimeField, IntegerField, HiddenInput, BooleanField
from django.forms.widgets import DateInput, DateTimeInput, TimeInput, DateTimeInput
from .models import GradingResult, Class, Member, Award, Payment, AssessmentUnit, GradingInvite, Grading, BELT_CHOICES, GRADINGS, LETTER_GRADES, ASSESSMENT_UNITS
from django.utils import timezone
from django import forms 
from django.urls import reverse_lazy

class GradingResultUpdateForm(ModelForm):
    is_letter = BooleanField(disabled=True, required=False)
    assessor = ModelMultipleChoiceField(queryset=Member.objects.all().exclude(team_leader_instructor__exact=''))

    class Meta:
        model = GradingResult
        fields = ['member','gradinginvite','grading','forbelt','assessor','comments','award', 'is_letter']

class GradingResultCreateForm(ModelForm):
    is_letter = BooleanField(required=False)
    assessor = ModelMultipleChoiceField(queryset=Member.objects.all().exclude(team_leader_instructor__exact=''))

    class Meta:
        model = GradingResult
        fields = ['member','gradinginvite','grading','forbelt','assessor','comments','award', 'is_letter']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
        }

class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = ['first_name','last_name','idnumber','address_line_1','address_line_2','address_line_3','date_of_birth','belt','email','phone','team_leader_instructor','active']
        widgets = {
            'phone': TextInput(attrs={'type': 'tel', 'placeholder': '0400 000 000'}),
            'date_of_birth': DateInput(attrs={'placeholder': 'yyyy-mm-dd'}),
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

    member = ModelChoiceField(queryset=Member.objects.all(), required=False)
    forbelt = ChoiceField(choices=BLANK_CHOICE + BELT_CHOICES, required=False, label='For Belt')
    assessor = ModelChoiceField(queryset=Member.objects.all(), required=False)
    award = ModelChoiceField(queryset=Award.objects.all(), required=False)
    type = ChoiceField(choices=BLANK_CHOICE + GRADINGS, required=False)
    date = DateField(required=False, widget=TextInput(attrs={
        'placeholder': 'YYYY-mm-dd'
    }))
    
class PaymentForm(ModelForm):
    date_created = DateTimeField(disabled=True, initial=timezone.now())

    class Meta:
        model = Payment
        fields = ['member', 'paymenttype', 'date_created', 'date_due', 'date_paid_in_full', 'amount_due', 'amount_paid']
        widgets = {
            'date_due': DateInput(attrs={'type': 'date'}),
            'date_paid_in_full': DateInput(attrs={'type':'date'}),
        }

class AssessmentUnitLetterForm(ModelForm):
    BLANK_CHOICE = [(None, '---------')]

    achieved_pts = ChoiceField(choices=enumerate(LETTER_GRADES), initial=4, required=False)
    max_pts = IntegerField(initial=7, widget=HiddenInput())
    unit = ChoiceField(choices= BLANK_CHOICE + ASSESSMENT_UNITS, required=False)
    class Meta:
        model = AssessmentUnit
        fields = ['unit', 'achieved_pts', 'max_pts']

class GradingInviteForm(ModelForm):   
    class Meta:
        model = GradingInvite
        fields = ['member', 'forbelt', 'grading', 'issued_by', 'payment']

class GradingForm(ModelForm):
    class Meta:
        model = Grading
        fields = ['grading_datetime', 'grading_type']
        widgets = {
            'grading_datetime': DateTimeInput(attrs={'type': 'datetime-local'}), 
        }
