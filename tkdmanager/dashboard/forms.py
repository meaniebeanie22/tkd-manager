from django import forms
from django.forms import (BooleanField, ChoiceField, DateField, DateTimeField,
                          Form, HiddenInput, IntegerField, ModelChoiceField,
                          ModelForm, ModelMultipleChoiceField,
                          MultipleChoiceField, TextInput)
from django.forms.widgets import (CheckboxSelectMultiple, DateInput,
                                  DateTimeInput, Select, TimeInput)
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django_addanother.widgets import (AddAnotherEditSelectedWidgetWrapper,
                                       AddAnotherWidgetWrapper)
from django_select2 import forms as s2forms

from .models import (LETTER_GRADES,
                     AssessmentUnit, Award, Class, Grading, GradingInvite,
                     GradingResult, Member, Payment, PaymentType,
                     RecurringPayment, MemberProperty, Belt, AssessmentUnitType,
                     GradingType, ClassType, Style)


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

class MemberPropertiesWidget(s2forms.ModelSelect2MultipleWidget):
    model = MemberProperty
    search_fields = [
        'name__icontains'
    ]
    queryset = MemberProperty.objects.filter(propertytype__searchable__exact=True).all()

class GradingResultUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingResultSearchForm, self).__init__(*args, **kwargs)
        self.fields["forbelt"].queryset = Belt.objects.filter(style__pk=self.request.session.get('pk', 1))
        self.fields["award"].queryset = Award.objects.filter(style__pk=self.request.session.get('pk', 1))
        self.fields["gradinginvite"].queryset = GradingInvite.objects.filter(grading__grading_type__style__pk=self.request.session.get('pk', 1))
        self.fields['grading'].queryset = Grading.objects.filter(grading_type__style__pk=self.request.session.get('pk', 1))

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
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingResultSearchForm, self).__init__(*args, **kwargs)
        self.fields["forbelt"].queryset = Belt.objects.filter(style__pk=self.request.session.get('pk', 1))
        self.fields["award"].queryset = Award.objects.filter(style__pk=self.request.session.get('pk', 1))
        self.fields["gradinginvite"].queryset = GradingInvite.objects.filter(grading__grading_type__style__pk=self.request.session.get('pk', 1))
        self.fields['grading'].queryset = Grading.objects.filter(grading_type__style__pk=self.request.session.get('pk', 1))
        

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
        fields = ['first_name','last_name','idnumber','address_line_1','address_line_2','address_line_3','date_of_birth','belt','email','phone','team_leader_instructor','active', 'properties']
        widgets = {
            'phone': TextInput(attrs={'type': 'tel', 'placeholder': '0400 000 000'}),
            'date_of_birth': DateInput(attrs={'placeholder': 'yyyy-mm-dd'}),
            'properties': MemberPropertiesWidget,
        }

class MemberSearchForm(Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(MemberSearchForm, self).__init__(*args, **kwargs)
        self.fields["belt"].queryset = Belt.objects.filter(style__pk=self.request.session.get('pk', 1))

    member = ModelChoiceField(required=False, queryset=Member.objects.all(), widget=MemberWidget)
    properties = ModelMultipleChoiceField(required=False, queryset = MemberProperty.objects.filter(propertytype__searchable__exact=True).all(), widget=MemberPropertiesWidget)
    belt = ModelChoiceField(queryset=Belt.objects.all(), required=False)

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
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ClassSearchForm, self).__init__(*args, **kwargs)
        self.fields["type"].queryset = ClassType.objects.filter(style__pk=self.request.session.get('pk', 1))

    type = ModelChoiceField(queryset=ClassType.objects.all(), required=False, widget=Select(attrs={
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
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingResultSearchForm, self).__init__(*args, **kwargs)
        self.fields["type"].queryset = GradingType.objects.filter(style__pk=self.request.session.get('pk', 1))
        self.fields["forbelt"].queryset = Belt.objects.filter(style__pk=self.request.session.get('pk', 1))
        self.fields["award"].queryset = Award.objects.filter(style__pk=self.request.session.get('pk', 1))

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
    forbelt = ModelChoiceField(queryset=Belt.objects.all(), required=False, label='For Belt')
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
    type = ModelChoiceField(queryset=GradingType.objects.all(), required=False)
    date = DateField(required=False, widget=TextInput(attrs={
        'placeholder': 'YYYY-mm-dd'
    }))

class GradingInviteSearchForm(Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingInviteSearchForm, self).__init__(*args, **kwargs)
        self.fields["type"].queryset = GradingType.objects.filter(style__pk=self.request.session.get('pk', 1))
        self.fields["forbelt"].queryset = Belt.objects.filter(style__pk=self.request.session.get('pk', 1))

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
    forbelt = ModelChoiceField(queryset=Belt.objects.all(), required=False, label='For Belt')
    type = ModelChoiceField(queryset=GradingType.objects.all(), required=False)
    date = DateField(required=False, widget=TextInput(attrs={
        'placeholder': 'YYYY-mm-dd'
    }))

class PaymentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields["paymenttype"].queryset = PaymentType.objects.filter(Q(style__pk=self.request.session.get('pk', 1)) | Q(style__pk__isnull=True))

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
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(PaymentSearchForm, self).__init__(*args, **kwargs)
        self.fields["paymenttype"].queryset = PaymentType.objects.filter(Q(style__pk=self.request.session.get('pk', 1)) | Q(style__pk__isnull=True))

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

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(AssessmentUnitLetterForm, self).__init__(*args, **kwargs)
        self.fields["unit"].queryset = AssessmentUnitType.objects.filter(style__pk=self.request.session.get('pk', 1))

    achieved_pts = ChoiceField(choices=enumerate(LETTER_GRADES), initial=4, required=False)
    max_pts = IntegerField(initial=7, widget=HiddenInput())
    unit = ModelChoiceField(queryset=AssessmentUnitType.objects.all(), required=False)
    class Meta:
        model = AssessmentUnit
        fields = ['unit', 'achieved_pts', 'max_pts']

class AssessmentUnitGradingResultForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(AssessmentUnitGradingResultForm, self).__init__(*args, **kwargs)
        self.fields["unit"].queryset = AssessmentUnitType.objects.filter(style__pk=self.request.session.get('pk', 1))

    class Meta:
        fields = ['unit', 'achieved_pts', 'max_pts']

class GradingInviteForm(ModelForm):  
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingInviteForm, self).__init__(*args, **kwargs)
        self.fields["grading"].queryset = Grading.objects.filter(style__pk=self.request.session.get('pk', 1))
        self.fields["forbelt"].queryset = Belt.objects.filter(style__pk=self.request.session.get('pk', 1))

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
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingForm, self).__init__(*args, **kwargs)
        self.fields["grading_type"].queryset = Grading.objects.filter(grading_type__style__pk=self.request.session.get('pk', 1))

    class Meta:
        model = Grading
        fields = ['grading_datetime', 'grading_type']
        widgets = {
            'grading_datetime': DateTimeInput(attrs={'type': 'datetime-local'}), 
        }

class RecurringPaymentUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(RecurringPaymentUpdateForm, self).__init__(*args, **kwargs)
        self.fields["paymenttype"].queryset = PaymentType.objects.filter(Q(style__pk=self.request.session.get('pk', 1)) | Q(style__pk__isnull=True))

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
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(RecurringPaymentForm, self).__init__(*args, **kwargs)
        self.fields["paymenttype"].queryset = PaymentType.objects.filter(Q(style__pk=self.request.session.get('pk', 1)) | Q(style__pk__isnull=True))

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
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(RecurringPaymentSearchForm, self).__init__(*args, **kwargs)
        self.fields["paymenttype"].queryset = PaymentType.objects.filter(Q(style__pk=self.request.session.get('pk', 1)) | Q(style__pk__isnull=True))

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
        fields = ['name', 'standard_amount', 'style']

class GradingSelectForm(Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingSelectForm, self).__init__(*args, **kwargs)
        self.fields["grading"].queryset = Grading.objects.filter(grading_type__style__pk=self.request.session.get('pk', 1))

    grading = ModelChoiceField(queryset = Grading.objects.all(), required=False)

class GradingInviteBulkForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingInviteBulkForm, self).__init__(*args, **kwargs)
        self.fields["grading"].queryset = Grading.objects.filter(grading_type__style__pk=self.request.session.get('pk', 1))
        self.fields["forbelt"].queryset = Belt.objects.filter(style__pk=self.request.session.get('pk', 1))

    grading = ModelChoiceField(queryset=Grading.objects.all(), required=False)
    class Meta:
        model = GradingInvite
        fields = ['member', 'forbelt', 'grading']
    
    select = BooleanField(required=False, initial=True)

    def has_changed(self):
        """
        Permit saving initial data
        """
        changed_data = super(ModelForm, self).has_changed()
        return bool(self.initial or changed_data)

class BeltForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'
            visible.field.widget.attrs['placeholder'] = visible.field.label
            
    class Meta:
        model = Belt
        fields = ['name']

class StyleForm(ModelForm):
    class Meta:
        model = Style
        fields = ['name']
