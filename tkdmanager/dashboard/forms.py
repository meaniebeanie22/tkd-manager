from django import forms
from django.forms import (
    BooleanField,
    ChoiceField,
    DateField,
    DateTimeField,
    Form,
    HiddenInput,
    IntegerField,
    ModelChoiceField,
    ModelForm,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    TextInput,
)
from django.forms.widgets import (
    CheckboxSelectMultiple,
    DateInput,
    DateTimeInput,
    Select,
    TimeInput,
)
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django_addanother.widgets import (
    AddAnotherEditSelectedWidgetWrapper,
    AddAnotherWidgetWrapper,
)
from django_select2 import forms as s2forms

from .models import (
    LETTER_GRADES,
    AssessmentUnit,
    Award,
    Class,
    Grading,
    GradingInvite,
    GradingResult,
    Member,
    Payment,
    PaymentType,
    RecurringPayment,
    MemberProperty,
    MemberPropertyType,
    Belt,
    AssessmentUnitType,
    GradingType,
    ClassType,
    Style,
)

from tkdmanager.forms import BSMixin
from django.forms.models import BaseInlineFormSet, inlineformset_factory
from django.utils.translation import gettext_lazy as _

from utils.forms import is_empty_form, is_form_persisted


class MembersWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "idnumber__istartswith",
    ]


class BeltsWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = ["style__name__icontains", "name__icontains"]


class MemberWidget(s2forms.ModelSelect2Widget):
    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "idnumber__istartswith",
    ]


class InstructorsWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "first_name__icontains",
        "last_name__icontains",
        "idnumber__istartswith",
    ]
    # members who have a property who's propertytype has teacher_property set to true - will need to be filtered to a specific style
    queryset = Member.objects.filter(
        properties__propertytype__teacher_property__exact=True
    ).all()


class MemberPropertiesWidget(s2forms.ModelSelect2MultipleWidget):
    model = MemberProperty
    search_fields = ["name__icontains"]
    queryset = MemberProperty.objects.filter(propertytype__searchable__exact=True).all()


class GradingResultUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingResultSearchForm, self).__init__(*args, **kwargs)
        self.fields["forbelt"].queryset = Belt.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )
        self.fields["award"].queryset = Award.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )
        self.fields["gradinginvite"].queryset = GradingInvite.objects.filter(
            grading__grading_type__style__pk=self.request.session.get("style", 1)
        )
        self.fields["grading"].queryset = Grading.objects.filter(
            grading_type__style__pk=self.request.session.get("style", 1)
        )

    is_letter = BooleanField(disabled=True, required=False)

    class Meta:
        model = GradingResult
        fields = [
            "member",
            "gradinginvite",
            "grading",
            "forbelt",
            "assessor",
            "comments",
            "award",
            "is_letter",
        ]
        widgets = {
            "member": MemberWidget,
            "assessor": InstructorsWidget,
            "gradinginvite": AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy("dash-add-grading-invite"),
                reverse_lazy("dash-update-grading-invite", kwargs={"pk": "__fk__"}),
            ),
            "award": AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy("dash-add-award"),
                reverse_lazy("dash-update-award", kwargs={"pk": "__fk__"}),
            ),
            "grading": AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy("dash-add-grading"),
                reverse_lazy("dash-update-grading", kwargs={"pk": "__fk__"}),
            ),
        }


class GradingResultCreateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingResultCreateForm, self).__init__(*args, **kwargs)
        self.fields["forbelt"].queryset = Belt.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )
        self.fields["award"].queryset = Award.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )
        self.fields["gradinginvite"].queryset = GradingInvite.objects.filter(
            grading__grading_type__style__pk=self.request.session.get("style", 1)
        )
        self.fields["grading"].queryset = Grading.objects.filter(
            grading_type__style__pk=self.request.session.get("style", 1)
        )

    is_letter = BooleanField(required=False)

    class Meta:
        model = GradingResult
        fields = [
            "member",
            "gradinginvite",
            "grading",
            "forbelt",
            "assessor",
            "comments",
            "award",
            "is_letter",
        ]
        widgets = {
            "member": MemberWidget,
            "assessor": InstructorsWidget,
            "gradinginvite": AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy("dash-add-grading-invite"),
                reverse_lazy("dash-update-grading-invite", kwargs={"pk": "__fk__"}),
            ),
            "award": AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy("dash-add-award"),
                reverse_lazy("dash-update-award", kwargs={"pk": "__fk__"}),
            ),
            "grading": AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy("dash-add-grading"),
                reverse_lazy("dash-update-grading", kwargs={"pk": "__fk__"}),
            ),
        }


class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = [
            "first_name",
            "last_name",
            "idnumber",
            "address_line_1",
            "address_line_2",
            "address_line_3",
            "date_of_birth",
            "belts",
            "email",
            "phone",
            "team_leader_instructor",
            "active",
            "properties",
        ]
        widgets = {
            "phone": TextInput(attrs={"type": "tel", "placeholder": "0400 000 000"}),
            "date_of_birth": DateInput(attrs={"placeholder": "yyyy-mm-dd"}),
            "properties": MemberPropertiesWidget,
        }


class MemberSearchForm(Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(MemberSearchForm, self).__init__(*args, **kwargs)
        self.fields["belt"].queryset = Belt.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )

    member = ModelChoiceField(
        required=False, queryset=Member.objects.all(), widget=MemberWidget
    )
    properties = ModelMultipleChoiceField(
        required=False,
        queryset=MemberProperty.objects.filter(
            propertytype__searchable__exact=True
        ).all(),
        widget=MemberPropertiesWidget,
    )
    belt = ModelChoiceField(queryset=Belt.objects.all(), required=False)


class ClassForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ClassForm, self).__init__(*args, **kwargs)
        self.fields["type"].queryset = ClassType.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )
        self.fields["instructors"].queryset = Member.objects.filter(
            Q(properties__propertytype__teacher_property__exact=True)
            & Q(
                properties__propertytype__style__pk=self.request.session.get("style", 1)
            )
        )
        self.fields["students"].queryset = Member.objects.filter(
            belts__style__pk=self.request.session.get("style", 1)
        )

    class Meta:
        model = Class
        fields = ["type", "date", "start", "end", "instructors", "students"]
        widgets = {
            "date": DateInput(attrs={"type": "date"}),
            "start": TimeInput(attrs={"type": "time"}),
            "end": TimeInput(attrs={"type": "time"}),
            "instructors": InstructorsWidget,
            "students": MembersWidget,
        }


class ClassSearchForm(Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(ClassSearchForm, self).__init__(*args, **kwargs)
        self.fields["type"].queryset = ClassType.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )

    type = ModelChoiceField(
        queryset=ClassType.objects.all(),
        required=False,
        widget=Select(attrs={"style": "max-width: 175px;"}),
    )
    date = DateField(
        required=False,
        widget=TextInput(attrs={"placeholder": "YYYY-mm-dd", "size": 10}),
    )
    instructor = ModelChoiceField(
        required=False,
        queryset=Member.objects.all().exclude(team_leader_instructor__exact=""),
        widget=s2forms.ModelSelect2Widget(
            model=Member,
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "idnumber__iexact",
            ],
        ),
    )
    student = ModelChoiceField(
        required=False,
        queryset=Member.objects.all(),
        widget=s2forms.ModelSelect2Widget(
            model=Member,
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "idnumber__iexact",
            ],
        ),
    )


class GradingResultSearchForm(Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingResultSearchForm, self).__init__(*args, **kwargs)
        self.fields["type"].queryset = GradingType.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )
        self.fields["forbelt"].queryset = Belt.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )
        self.fields["award"].queryset = Award.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )

    member = ModelChoiceField(
        required=False,
        queryset=Member.objects.all(),
        widget=s2forms.ModelSelect2Widget(
            model=Member,
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "idnumber__iexact",
            ],
        ),
    )
    forbelt = ModelChoiceField(
        queryset=Belt.objects.all(), required=False, label="For Belt"
    )
    assesor = ModelChoiceField(
        required=False,
        queryset=Member.objects.all().exclude(team_leader_instructor__exact=""),
        widget=s2forms.ModelSelect2Widget(
            model=Member,
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "idnumber__iexact",
            ],
        ),
    )
    award = ModelChoiceField(queryset=Award.objects.all(), required=False)
    type = ModelChoiceField(queryset=GradingType.objects.all(), required=False)
    date = DateField(
        required=False, widget=TextInput(attrs={"placeholder": "YYYY-mm-dd"})
    )


class GradingInviteSearchForm(Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingInviteSearchForm, self).__init__(*args, **kwargs)
        self.fields["type"].queryset = GradingType.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )
        self.fields["forbelt"].queryset = Belt.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )

    member = ModelChoiceField(
        required=False,
        queryset=Member.objects.all(),
        widget=s2forms.ModelSelect2Widget(
            model=Member,
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "idnumber__iexact",
            ],
        ),
    )
    forbelt = ModelChoiceField(
        queryset=Belt.objects.all(), required=False, label="For Belt"
    )
    type = ModelChoiceField(queryset=GradingType.objects.all(), required=False)
    date = DateField(
        required=False, widget=TextInput(attrs={"placeholder": "YYYY-mm-dd"})
    )


class PaymentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields["paymenttype"].queryset = PaymentType.objects.filter(
            Q(style__pk=self.request.session.get("style", 1))
            | Q(style__pk__isnull=True)
        )

    date_created = DateTimeField(disabled=True, initial=timezone.now())

    class Meta:
        model = Payment
        fields = [
            "member",
            "paymenttype",
            "date_created",
            "date_due",
            "date_paid_in_full",
            "amount_due",
            "amount_paid",
        ]
        widgets = {
            "date_due": DateInput(attrs={"type": "date"}),
            "date_paid_in_full": DateInput(attrs={"type": "date"}),
            "member": MemberWidget,
            "paymenttype": AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy("dash-add-payment-type"),
                reverse_lazy("dash-update-payment-type", kwargs={"pk": "__fk__"}),
            ),
        }


class PaymentSearchForm(Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(PaymentSearchForm, self).__init__(*args, **kwargs)
        self.fields["paymenttype"].queryset = PaymentType.objects.filter(
            Q(style__pk=self.request.session.get("style", 1))
            | Q(style__pk__isnull=True)
        )

    member = ModelChoiceField(
        required=False,
        queryset=Member.objects.all(),
        widget=s2forms.ModelSelect2Widget(
            model=Member,
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "idnumber__iexact",
            ],
        ),
    )
    paymenttype = ModelChoiceField(
        queryset=PaymentType.objects.all(),
        required=False,
        label="Payment Type",
        widget=Select(attrs={"style": "max-width: 175px;"}),
    )
    date_created = DateField(
        required=False,
        widget=TextInput(attrs={"placeholder": "YYYY-mm-dd", "size": 10}),
    )
    date_due = DateField(
        required=False,
        widget=TextInput(attrs={"placeholder": "YYYY-mm-dd", "size": 10}),
    )
    selected_statuses = MultipleChoiceField(
        choices=(
            ("Overdue", "Overdue"),
            ("Awaiting Payment", "Awaiting Payment"),
            ("Paid Late", "Paid Late"),
            ("Paid On Time", "Paid On Time"),
        ),
        required=False,
        widget=CheckboxSelectMultiple(),
    )


class AssessmentUnitLetterForm(ModelForm):
    BLANK_CHOICE = [(None, "---------")]

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(AssessmentUnitLetterForm, self).__init__(*args, **kwargs)
        self.fields["unit"].queryset = AssessmentUnitType.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )

    achieved_pts = ChoiceField(
        choices=enumerate(LETTER_GRADES), initial=4, required=False
    )
    max_pts = IntegerField(initial=7, widget=HiddenInput())
    unit = ModelChoiceField(queryset=AssessmentUnitType.objects.all(), required=False)

    class Meta:
        model = AssessmentUnit
        fields = ["unit", "achieved_pts", "max_pts"]


class AssessmentUnitGradingResultForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(AssessmentUnitGradingResultForm, self).__init__(*args, **kwargs)
        self.fields["unit"].queryset = AssessmentUnitType.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )

    class Meta:
        fields = ["unit", "achieved_pts", "max_pts"]


class GradingInviteForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingInviteForm, self).__init__(*args, **kwargs)
        self.fields["grading"].queryset = Grading.objects.filter(
            grading_type__style__pk=self.request.session.get("style", 1)
        )
        self.fields["forbelt"].queryset = Belt.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )

    class Meta:
        model = GradingInvite
        fields = ["member", "forbelt", "grading", "issued_by", "payment"]
        widgets = {
            "member": MemberWidget,
            "payment": AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy("dash-add-payment"),
                reverse_lazy("dash-update-payment", kwargs={"pk": "__fk__"}),
            ),
            "grading": AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy("dash-add-grading"),
                reverse_lazy("dash-update-grading", kwargs={"pk": "__fk__"}),
            ),
        }


class GradingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingForm, self).__init__(*args, **kwargs)
        self.fields["grading_type"].queryset = Grading.objects.filter(
            grading_type__style__pk=self.request.session.get("style", 1)
        )

    class Meta:
        model = Grading
        fields = ["grading_datetime", "grading_type"]
        widgets = {
            "grading_datetime": DateTimeInput(attrs={"type": "datetime-local"}),
        }


class RecurringPaymentUpdateForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(RecurringPaymentUpdateForm, self).__init__(*args, **kwargs)
        self.fields["paymenttype"].queryset = PaymentType.objects.filter(
            Q(style__pk=self.request.session.get("style", 1))
            | Q(style__pk__isnull=True)
        )

    class Meta:
        model = RecurringPayment
        fields = ["member", "payments", "interval", "amount", "paymenttype"]
        widgets = {
            "member": MemberWidget,
            "payments": AddAnotherWidgetWrapper(
                forms.SelectMultiple,
                reverse_lazy("dash-add-payment"),
            ),
            "last_payment_date": TextInput(
                attrs={
                    "placeholder": "YYYY-mm-dd",
                    "size": 10,
                }
            ),
        }


class RecurringPaymentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(RecurringPaymentForm, self).__init__(*args, **kwargs)
        self.fields["paymenttype"].queryset = PaymentType.objects.filter(
            Q(style__pk=self.request.session.get("style", 1))
            | Q(style__pk__isnull=True)
        )

    class Meta:
        model = RecurringPayment
        fields = ["member", "interval", "amount", "paymenttype"]
        widgets = {
            "member": MemberWidget,
            "paymenttype": AddAnotherEditSelectedWidgetWrapper(
                forms.Select,
                reverse_lazy("dash-add-payment-type"),
                reverse_lazy("dash-update-payment-type", kwargs={"pk": "__fk__"}),
            ),
        }


class RecurringPaymentSearchForm(Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(RecurringPaymentSearchForm, self).__init__(*args, **kwargs)
        self.fields["paymenttype"].queryset = PaymentType.objects.filter(
            Q(style__pk=self.request.session.get("style", 1))
            | Q(style__pk__isnull=True)
        )

    member = ModelMultipleChoiceField(
        queryset=Member.objects.all(), required=False, widget=MemberWidget
    )
    last_payment_date = DateField(
        required=False,
        widget=TextInput(attrs={"placeholder": "YYYY-mm-dd", "size": 10}),
    )
    next_due = DateField(
        required=False,
        widget=TextInput(attrs={"placeholder": "YYYY-mm-dd", "size": 10}),
    )
    paymenttype = ModelChoiceField(
        queryset=PaymentType.objects.all(),
        required=False,
        label="Payment Type",
        widget=Select(attrs={"style": "max-width: 175px;"}),
    )


class PaymentTypeForm(ModelForm):
    class Meta:
        model = PaymentType
        fields = ["name", "standard_amount", "style"]


class GradingSelectForm(Form):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingSelectForm, self).__init__(*args, **kwargs)
        self.fields["grading"].queryset = Grading.objects.filter(
            grading_type__style__pk=self.request.session.get("style", 1)
        )

    grading = ModelChoiceField(queryset=Grading.objects.all(), required=False)


class GradingInviteBulkForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        super(GradingInviteBulkForm, self).__init__(*args, **kwargs)
        self.fields["grading"].queryset = Grading.objects.filter(
            grading_type__style__pk=self.request.session.get("style", 1)
        )
        self.fields["forbelt"].queryset = Belt.objects.filter(
            style__pk=self.request.session.get("style", 1)
        )

    grading = ModelChoiceField(queryset=Grading.objects.all(), required=False)

    class Meta:
        model = GradingInvite
        fields = ["member", "forbelt", "grading"]

    select = BooleanField(required=False, initial=True)

    def has_changed(self):
        """
        Permit saving initial data
        """
        changed_data = super(ModelForm, self).has_changed()
        return bool(self.initial or changed_data)


class BeltForm(BSMixin, ModelForm):
    class Meta:
        model = Belt
        fields = ["name"]


class StyleForm(BSMixin, ModelForm):
    class Meta:
        model = Style
        fields = ["name"]


class AssessmentUnitTypeForm(BSMixin, ModelForm):
    class Meta:
        model = AssessmentUnitType
        fields = ["name", "style"]


class ClassTypeForm(BSMixin, ModelForm):
    class Meta:
        model = ClassType
        fields = ["name", "style"]


class GradingTypeForm(BSMixin, ModelForm):
    class Meta:
        model = GradingType
        fields = ["name", "style"]

class AwardForm(BSMixin, ModelForm):
    class Meta:
        model = Award
        fields = ["name"]

# The formset for editing the BookImages that belong to a Book.
MemberPropertyFormset = inlineformset_factory(
    MemberPropertyType, MemberProperty, fields=("name",), extra=1
)


class BaseMPTsWithMPsFormset(BaseInlineFormSet):
    """
    The base formset for editing MemberPropertyTypes belonging to a style and their MemberProperties
    """

    def add_fields(self, form, index):
        super().add_fields(form, index)

        # Save the formset for an MPT's MP's in the nested property.
        form.nested = MemberPropertyFormset(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix="memberproperty-%s-%s"
            % (form.prefix, MemberPropertyFormset.get_default_prefix()),
        )

    def is_valid(self):
        """
        Also validate the nested formsets.
        """
        result = super().is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, "nested"):
                    result = result and form.nested.is_valid()

        return result

    def clean(self):
        """
        If a parent form has no data, but its nested forms do, we should
        return an error, because we can't save the parent.
        For example, if the MPT form is empty, but there are MPs.
        """
        super().clean()

        for form in self.forms:
            if not hasattr(form, "nested") or self._should_delete_form(form):
                continue

            if self._is_adding_nested_inlines_to_empty_form(form):
                form.add_error(
                    field=None,
                    error=_(
                        "You are trying to add property(ies) to a property type which "
                        "does not yet exist. Please add information "
                        "about the property type and enter the properties again."
                    ),
                )

    def save(self, commit=True):
        """
        Also save the nested formsets.
        """
        result = super().save(commit=commit)

        for form in self.forms:
            if hasattr(form, "nested"):
                if not self._should_delete_form(form):
                    form.nested.save(commit=commit)

        return result

    def _is_adding_nested_inlines_to_empty_form(self, form):
        """
        Are we trying to add data in nested inlines to a form that has no data?
        e.g. Adding properties to a new propertytype whose data we haven't entered?
        """
        if not hasattr(form, "nested"):
            # A basic form; it has no nested forms to check.
            return False

        if is_form_persisted(form):
            # We're editing (not adding) an existing model.
            return False

        if not is_empty_form(form):
            # The form has errors, or it contains valid data.
            return False

        # All the inline forms that aren't being deleted:
        non_deleted_forms = set(form.nested.forms).difference(
            set(form.nested.deleted_forms)
        )

        # At this point we know that the "form" is empty.
        # In all the inline forms that aren't being deleted, are there any that
        # contain data? Return True if so.
        return any(not is_empty_form(nested_form) for nested_form in non_deleted_forms)


# This is the formset for the propertytypes belonging to a style and the
# property belonging to those propertytypes.
#
# You'd use this by passing in a Style:
#     StyleMPTswithMPsFormset(**form_kwargs, instance=self.object)

        