from django import forms
from django.forms import (BooleanField, ChoiceField, DateField, DateTimeField,
                          Form, HiddenInput, IntegerField, ModelChoiceField,
                          ModelForm, ModelMultipleChoiceField,
                          MultipleChoiceField, TextInput)
from django.forms.widgets import (CheckboxSelectMultiple, DateInput,
                                  DateTimeInput, Select, TimeInput)
from django.urls import reverse_lazy
from django.utils import timezone
from django_addanother.widgets import (AddAnotherEditSelectedWidgetWrapper,
                                       AddAnotherWidgetWrapper)
from django_select2 import forms as s2forms

from .models import (ASSESSMENT_UNITS, BELT_CHOICES, GRADINGS, LETTER_GRADES,
                     AssessmentUnit, Award, Class, Grading, GradingInvite,
                     GradingResult, Member, Payment, PaymentType,
                     RecurringPayment)


class MembersWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
        'idnumber__istartswith'
    ]

class MemberWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
        'idnumber__istartswith'
    ]

class InstructorsWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        'first_name__icontains',
        'last_name__icontains',
        'idnumber__istartswith'
    ]
    queryset = Member.objects.all().exclude(team_leader_instructor__exact='')

class GradingResultUpdateForm(ModelForm):
    is_letter = BooleanField(disabled=True, required=False)

    class Meta:
        model = GradingResult
        fields = ['member','gradinginvite','grading','forbelt','assessor','comments','award', 'is_letter']
        widgets = {
            'member': MemberWidget,
            'assessor': InstructorsWidget,
            'gradinginvite': AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy('dash-add-grading-invite'),
                reverse_lazy('dash-update-grading-invite',kwargs={'pk': '__fk__'}),
            ),
            'award': AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy('dash-add-award'),
                reverse_lazy('dash-update-award',kwargs={'pk': '__fk__'}),
            ),
            'grading': AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy('dash-add-grading'),
                reverse_lazy('dash-update-grading',kwargs={'pk': '__fk__'}),
            ),
        }

class GradingResultCreateForm(ModelForm):
    is_letter = BooleanField(required=False)

    class Meta:
        model = GradingResult
        fields = ['member','gradinginvite','grading','forbelt','assessor','comments','award', 'is_letter']
        widgets = {
            'member': MemberWidget,
            'assessor': InstructorsWidget,
            'gradinginvite': AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy('dash-add-grading-invite'),
                reverse_lazy('dash-update-grading-invite',kwargs={'pk': '__fk__'}),
            ),
            'award': AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy('dash-add-award'),
                reverse_lazy('dash-update-award',kwargs={'pk': '__fk__'}),
            ),
            'grading': AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy('dash-add-grading'),
                reverse_lazy('dash-update-grading',kwargs={'pk': '__fk__'}),
            ),
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
    class Meta:
        model = Class
        fields = ['type','date','start','end','instructors','students']
        widgets = {
            'date': DateInput(attrs={'type': 'date'}),
            'start': TimeInput(attrs={'type': 'time'}),
            'end': TimeInput(attrs={'type': 'time'}),
            'instructors': InstructorsWidget,
            'students': MembersWidget,
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
    instructor = ModelChoiceField(required=False, 
        queryset=Member.objects.all().exclude(team_leader_instructor__exact=''),
        widget=s2forms.ModelSelect2Widget(
            model=Member, 
            search_fields = [
                'first_name__icontains',
                'last_name__icontains',
                'idnumber__iexact'
            ]
        )
    )
    student = ModelChoiceField(required=False, queryset=Member.objects.all(),
        widget=s2forms.ModelSelect2Widget(
            model=Member, 
            search_fields = [
                'first_name__icontains',
                'last_name__icontains',
                'idnumber__iexact'
            ],
        )
    )

class GradingResultSearchForm(Form):
    BLANK_CHOICE = [('', '---------')]

    member = ModelChoiceField(required=False, queryset=Member.objects.all(),
        widget=s2forms.ModelSelect2Widget(
            model=Member, 
            search_fields = [
                'first_name__icontains',
                'last_name__icontains',
                'idnumber__iexact'
            ]
        )
    )
    forbelt = ChoiceField(choices=BLANK_CHOICE + BELT_CHOICES, required=False, label='For Belt')
    assesor = ModelChoiceField(required=False, queryset=Member.objects.all().exclude(team_leader_instructor__exact=''),
        widget=s2forms.ModelSelect2Widget(
            model=Member, 
            search_fields = [
                'first_name__icontains',
                'last_name__icontains',
                'idnumber__iexact'
            ]
        )
    )
    award = ModelChoiceField(queryset=Award.objects.all(), required=False)
    type = ChoiceField(choices=BLANK_CHOICE + GRADINGS, required=False)
    date = DateField(required=False, widget=TextInput(attrs={
        'placeholder': 'YYYY-mm-dd'
    }))

class GradingInviteSearchForm(Form):
    BLANK_CHOICE = [('', '---------')]

    member = ModelChoiceField(required=False, queryset=Member.objects.all(),
        widget=s2forms.ModelSelect2Widget(
            model=Member, 
            search_fields = [
                'first_name__icontains',
                'last_name__icontains',
                'idnumber__iexact'
            ],
        )
    )
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
            'member': MemberWidget,
            'paymenttype': AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy('dash-add-payment-type'),
                reverse_lazy('dash-update-payment-type',kwargs={'pk': '__fk__'}),
            ),
        }

class PaymentSearchForm(Form):
    member = ModelChoiceField(required=False, queryset=Member.objects.all(),
        widget=s2forms.ModelSelect2Widget(
            model=Member, 
            search_fields = [
                'first_name__icontains',
                'last_name__icontains',
                'idnumber__iexact'
            ],
        )
    )
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
    selected_statuses = MultipleChoiceField(choices=(
            ('Overdue', 'Overdue'),
            ('Awaiting Payment', 'Awaiting Payment'),
            ('Paid Late', 'Paid Late'),
            ('Paid On Time', 'Paid On Time'),            
        ),
        required=False,
        widget=CheckboxSelectMultiple()
    )

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
        widgets = {
            'member': MemberWidget,
            'payment': AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy('dash-add-payment'),
                reverse_lazy('dash-update-payment',kwargs={'pk': '__fk__'}),
            ),
            'grading': AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy('dash-add-grading'),
                reverse_lazy('dash-update-grading',kwargs={'pk': '__fk__'}),
            ), 
        }
        
class GradingForm(ModelForm):
    class Meta:
        model = Grading
        fields = ['grading_datetime', 'grading_type']
        widgets = {
            'grading_datetime': DateTimeInput(attrs={'type': 'datetime-local'}), 
        }

class RecurringPaymentUpdateForm(ModelForm):
    class Meta:
        model = RecurringPayment
        fields = ['member','payments','interval','amount','paymenttype']
        widgets = {
            'member': MemberWidget,
            'payments': AddAnotherWidgetWrapper(
                forms.SelectMultiple,
                reverse_lazy('dash-add-payment'),
            ),
            'last_payment_date': TextInput(attrs={
                'placeholder': 'YYYY-mm-dd',
                'size': 10,
            }),
        }

class RecurringPaymentForm(ModelForm):
    class Meta:
        model = RecurringPayment
        fields = ['member','interval','amount','paymenttype']
        widgets = {
            'member': MemberWidget,
            'paymenttype': AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy('dash-add-payment-type'),
                reverse_lazy('dash-update-payment-type',kwargs={'pk': '__fk__'}),
            ),
        }

class RecurringPaymentSearchForm(Form):
    member = ModelMultipleChoiceField(queryset=Member.objects.all(), required=False, widget=MemberWidget)
    last_payment_date = DateField(required=False, widget=TextInput(attrs={
        'placeholder': 'YYYY-mm-dd',
        'size': 10
    }))
    next_due = DateField(required=False, widget=TextInput(attrs={
        'placeholder': 'YYYY-mm-dd',
        'size': 10
    }))
    paymenttype = ModelChoiceField(queryset=PaymentType.objects.all(), required=False, label='Payment Type', widget=Select(attrs={
        'style':'max-width: 175px;'
    }))
        
class PaymentTypeForm(ModelForm):
    class Meta:
        model = PaymentType
        fields = ['name','standard_amount']
