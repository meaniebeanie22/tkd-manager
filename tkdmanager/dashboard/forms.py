from django.forms import ModelForm, ChoiceField, DateField, ModelChoiceField, ModelMultipleChoiceField, TextInput, Form, DateTimeField, IntegerField, HiddenInput, BooleanField
from django.forms.widgets import DateInput, DateTimeInput, TimeInput, DateTimeInput, Select
from .models import GradingResult, Class, Member, Award, Payment, AssessmentUnit, GradingInvite, Grading, PaymentType, BELT_CHOICES, GRADINGS, LETTER_GRADES, ASSESSMENT_UNITS
from django.utils import timezone
from django import forms 
from django.urls import reverse_lazy
from django_select2 import forms as s2forms

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

class StudentsWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
        'idnumber__iexact'
    ]

class InstructorsWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
        'idnumber__iexact'
    ]
    queryset = Member.objects.all().exclude(team_leader_instructor__exact='')

class ClassForm(ModelForm):
    #instructors = ModelMultipleChoiceField(queryset=Member.objects.all().exclude(team_leader_instructor__exact=''))

    class Meta:
        model = Class
        fields = ['type','date','start','end','instructors','students']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
            'start': TimeInput(attrs={'type': 'time'}),
            'end': TimeInput(attrs={'type': 'time'}),
            'instructors': InstructorsWidget,
            'students': StudentsWidget,
        }

class ClassSearchForm(Form):
    BLANK_CHOICE = [('', '---------')]

    type = ChoiceField(choices=BLANK_CHOICE + GRADINGS, required=False, widget=Select(attrs={
        'style':'max-width: 175px;'
    }))
    date = DateField(required=False, widget=TextInput(attrs={
        'placeholder': 'YYYY-mm-dd',
        'size': 10
    }))
    instructors = ModelMultipleChoiceField(required=False, queryset = Member.objects.all().exclude(team_leader_instructor__exact=''),
        widget=s2forms.ModelSelect2MultipleWidget(
            model=Member, 
            search_fields = [
                'first_name__icontains',
                'last_name__icontains',
                'idnumber__iexact'
            ]
        )
    )
    students = ModelMultipleChoiceField(required=False, queryset=Member.objects.all(),
        widget=s2forms.ModelSelect2MultipleWidget(
            model=Member, 
            search_fields = [
                'first_name__icontains',
                'last_name__icontains',
                'idnumber__iexact'
            ],
            queryset=Member.objects.all()
        )
    )

class GradingResultSearchForm(Form):
    BLANK_CHOICE = [('', '---------')]

    member = ModelChoiceField(queryset=Member.objects.all(), required=False)
    forbelt = ChoiceField(choices=BLANK_CHOICE + BELT_CHOICES, required=False, label='For Belt')
    assessor = ModelChoiceField(queryset=Member.objects.exclude(team_leader_instructor__exact='').all(), required=False)
    award = ModelChoiceField(queryset=Award.objects.all(), required=False)
    type = ChoiceField(choices=BLANK_CHOICE + GRADINGS, required=False)
    date = DateField(required=False, widget=TextInput(attrs={
        'placeholder': 'YYYY-mm-dd'
    }))

class GradingInviteSearchForm(Form):
    BLANK_CHOICE = [('', '---------')]

    member = ModelChoiceField(queryset=Member.objects.all(), required=False)
    forbelt = ChoiceField(choices=BLANK_CHOICE + BELT_CHOICES, required=False, label='For Belt')
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

class PaymentSearchForm(Form):
    member = ModelChoiceField(queryset=Member.objects.all(), required=False)
    paymenttype = ModelChoiceField(queryset=PaymentType.objects.all(), required=False, label='Payment Type', widget=Select(attrs={
        'style':'max-width: 175px;'
    }))
    date_created = DateField(required=False, widget=TextInput(attrs={
        'placeholder': 'YYYY-mm-dd',
        'size': 10
    }))
    date_due = DateField(required=False, widget=TextInput(attrs={
        'placeholder': 'YYYY-mm-dd',
        'size': 10
    }))



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
