from datetime import datetime, timedelta
from io import BytesIO
from typing import Any
from convenient_formsets import ConvenientBaseModelFormSet, ConvenientBaseInlineFormSet

from dashboard import renderers
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
)
from django.core import mail
from django.db.models import Q, Case, When, Value
from django.db import models, transaction

from django.forms import inlineformset_factory, modelformset_factory
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import View, generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from pypdf import PdfReader, PdfWriter
from rest_framework.authtoken.models import Token

from .forms import *
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
    Belt,
    AssessmentUnitType,
    Style,
    MemberPropertyType,
)
from .mixins import MFARequiredMixin
from .decorators import mfa_required


def order_members_by_belt_from_style(
    selected_style_id: int, queryset=Member.objects.all()
):
    """
    THIS IS UGLY AS HELL AND NEEDS TO BE FIXED
    Does what it says on the tin
    """

    m_rank = []
    for m in queryset:
        if belt := m.belts.filter(style__pk=selected_style_id):
            m_rank.append((m, belt.first().degree))
    m_rank.sort(key=lambda x: -x[1])

    my_ids = [x[0].pk for x in m_rank]

    return Member.objects.filter(pk__in=my_ids).order_by(
        Case(
            *[When(pk=pk, then=Value(i)) for i, pk in enumerate(my_ids)],
            output_field=models.IntegerField(),
        ).asc()
    )


def time_difference_in_seconds(time1, time2):
    # Convert time objects to timedelta
    delta = datetime.combine(timezone.now().date(), time2) - datetime.combine(
        timezone.now().date(), time1
    )
    # Calculate the time difference in seconds
    difference_seconds = delta.total_seconds()
    return difference_seconds


# Create your views here.
@login_required
@mfa_required
def index(request):
    """homepage"""

    # Number of members
    num_members = Member.objects.count()
    num_active_members = Member.objects.filter(active__exact=True).count()
    belts = Belt.objects.filter(style__pk=request.session.get("style", 1))
    labels = [belt.name for belt in belts]
    counts = [belt.belts.count() for belt in belts]

    context = {
        "num_members": num_members,
        "num_active_members": num_active_members,
        "belt_labels": labels,
        "belt_count": counts,
    }

    return render(request, "home.html", context=context)


@permission_required("authtoken.add_token")
@mfa_required
def token_display(request):
    token, created = Token.objects.get_or_create(user=request.user)
    context = {"token": token.key}

    return render(request, "token.html", context=context)


@permission_required("authtoken.delete_token")
@mfa_required
def token_delete(request):
    token = get_object_or_404(Token, user=request.user)
    token.delete()
    return HttpResponseRedirect(reverse_lazy("dash-get-token"))


class MemberListView(MFARequiredMixin, LoginRequiredMixin, generic.ListView):
    model = Member
    ordering = ["-belts", "last_name"]

    def get_queryset(self):
        queryset = Member.objects.all()

        # Process form data to filter queryset
        form = MemberSearchForm(self.request.GET, request=self.request)
        if form.is_valid():
            filters = {}

            # Iterate over form fields and add filters dynamically
            for field_name, value in form.cleaned_data.items():
                if field_name == "member" and value:
                    queryset = Member.objects.filter(pk=value.pk).all()
                    return queryset
                if value:
                    filters[field_name] = value

            # Apply all filters to the queryset in a single call
            queryset = queryset.filter(**filters)

        return order_members_by_belt_from_style(
            self.request.session.get("style", 1), queryset
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = MemberSearchForm(
            self.request.GET, request=self.request
        )
        return context


class MemberDetailView(MFARequiredMixin, LoginRequiredMixin, generic.DetailView):
    model = Member

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(MemberDetailView, self).get_context_data(**kwargs)

        # Find no. hours taught
        classes_taught = self.get_object().instructors2classes.all()

        # Use sum with a generator expression to calculate total seconds
        total_seconds = sum(
            time_difference_in_seconds(cl.start, cl.end) for cl in classes_taught
        )

        # Calculate hours directly from total seconds
        hours = round(total_seconds / 3600, 2)

        context["hours_taught"] = hours

        # Find overdue payments + those for the next 6 months
        today = timezone.now().date()
        six_months_later = today + timedelta(days=6 * 30)
        six_months_before = today - timedelta(days=6 * 30)
        recent_payments = (
            self.get_object()
            .payment_set.filter(
                Q(date_due__date__gte=six_months_before)
                & Q(date_due__date__lte=six_months_later)
            )
            .all()
        )
        payments = self.get_object().payment_set.all()
        overdue_payments = [p for p in payments if p.payment_status == "Overdue"]
        context["relevant_payments"] = list(recent_payments) + overdue_payments
        return context


class GradingResultDetailView(MFARequiredMixin, LoginRequiredMixin, generic.DetailView):
    model = GradingResult

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(GradingResultDetailView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        gr = self.get_object()
        assessmentunits = gr.assessmentunit_set.all()
        if assessmentunits:
            maxpts = 0
            apts = 0
            for au in assessmentunits:
                maxpts += au.max_pts
                apts += au.achieved_pts
            if gr.is_letter:
                context["average_grade"] = LETTER_GRADES[
                    round(apts / (len(assessmentunits)))
                ]
            else:
                context["total_max_pts"] = maxpts
                context["total_achieved_pts"] = apts
                context["total_percent"] = round(
                    (context["total_achieved_pts"] / context["total_max_pts"]) * 100
                )

        return context


class GradingResultListView(MFARequiredMixin, LoginRequiredMixin, generic.ListView):
    model = GradingResult

    def get_queryset(self):
        queryset = GradingResult.objects.filter(
            grading__grading_type__style__pk=self.request.session.get("style", 1)
        ).all()

        # Process form data to filter queryset
        form = GradingResultSearchForm(self.request.GET, request=self.request)
        if form.is_valid():
            filters = {}

            # Iterate over form fields and add filters dynamically
            for field_name, value in form.cleaned_data.items():
                if field_name == "date" and value:
                    filters["grading__grading_datetime__date"] = value
                elif field_name == "type" and value:
                    filters["grading__grading_type"] = value
                else:
                    if value:
                        filters[field_name] = value

            # Apply all filters to the queryset in a single call
            queryset = queryset.filter(**filters)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = GradingResultSearchForm(
            self.request.GET, request=self.request
        )
        return context


class MemberCreate(MFARequiredMixin, LoginRequiredMixin, CreateView):
    model = Member
    form_class = MemberForm


class MemberUpdate(MFARequiredMixin, LoginRequiredMixin, UpdateView):
    model = Member
    form_class = MemberForm


class MemberDelete(MFARequiredMixin, LoginRequiredMixin, DeleteView):
    model = Member
    success_url = reverse_lazy("dash-members")


class GradingResultCreate(MFARequiredMixin, LoginRequiredMixin, CreateView):
    form_class = GradingResultCreateForm
    model = GradingResult
    template_name = "dashboard/gradingresult_form.html"

    def form_valid(self, form):
        response = super(GradingResultCreate, self).form_valid(form)
        # do something with self.object
        target = self.object.member
        target.belt = (
            target.member2gradings.order_by("-grading__grading_datetime")
            .filter(style__pk=self.request.get("style", 1))
            .first()
            .forbelt
        )
        target.save()
        return response

    def get_success_url(self):
        if self.object.is_letter:
            return reverse("dash-update-grading-result3", kwargs={"pk": self.object.pk})
        else:
            return reverse("dash-update-grading-result2", kwargs={"pk": self.object.pk})

    def get_initial(self):
        # Autofill the member field based on the 'member_id' parameter in the URL
        member_id = self.request.GET.get("member_id")
        i = {}
        if member_id:
            i["member"] = member_id
            i["forbelt"] = get_object_or_404(
                Belt, pk=(Member.objects.get(id=member_id).belt.pk + 1)
            )
        return i

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class GradingResultUpdate(MFARequiredMixin, LoginRequiredMixin, UpdateView):
    form_class = GradingResultUpdateForm
    template_name = "dashboard/gradingresult_form.html"
    model = GradingResult

    def form_valid(self, form):
        response = super(GradingResultUpdate, self).form_valid(form)
        # do something with self.object
        target = self.object.member
        target.belt = (
            target.member2gradings.order_by("-grading__grading_datetime")
            .first()
            .forbelt
        )
        target.save()
        return response

    def get_success_url(self):
        if self.object.is_letter:
            return reverse("dash-update-grading-result3", kwargs={"pk": self.object.pk})
        else:
            return reverse("dash-update-grading-result2", kwargs={"pk": self.object.pk})

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class GradingResultDelete(MFARequiredMixin, LoginRequiredMixin, DeleteView):
    model = GradingResult
    success_url = reverse_lazy("dash-gradingresults")


class AwardListView(MFARequiredMixin, LoginRequiredMixin, generic.ListView):
    model = Award

    def get_queryset(self):
        queryset = Award.objects.filter(
            style__pk=self.request.session.get("style", 1)
        ).all()
        return queryset


class AwardCreate(CreatePopupMixin, MFARequiredMixin, LoginRequiredMixin, CreateView):
    model = Award
    form_class = AwardForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get("_popup", False)
        c["popup"] = popup
        return c

    def form_valid(self, form):
        response = super(AwardCreate, self).form_valid(form)
        self.object.style = self.request.session.get("style", 1)
        self.object.save()
        return response


class AwardUpdate(UpdatePopupMixin, MFARequiredMixin, LoginRequiredMixin, UpdateView):
    model = Award
    form_class = AwardForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get("_popup", False)
        c["popup"] = popup
        return c

    def form_valid(self, form):
        response = super(AwardCreate, self).form_valid(form)
        self.object.style = self.request.session.get("style", 1)
        self.object.save()
        return response


class AwardDelete(MFARequiredMixin, LoginRequiredMixin, DeleteView):
    model = Award
    success_url = reverse_lazy("dash-awards")


class AwardDetailView(MFARequiredMixin, LoginRequiredMixin, generic.DetailView):
    model = Award


@mfa_required
@permission_required("dashboard.change_gradingresult")
def manageGradingResult(request, **kwargs):
    gradingresult = GradingResult.objects.get(pk=kwargs["pk"])
    AssessmentUnitInlineFormSet = inlineformset_factory(
        GradingResult,
        AssessmentUnit,
        form=AssessmentUnitGradingResultForm,
        extra=10 - gradingresult.assessmentunit_set.all().count(),
    )

    if request.method == "POST":
        formset = AssessmentUnitInlineFormSet(
            request.POST,
            request.FILES,
            instance=gradingresult,
            form_kwargs={"request": request},
        )
        if formset.is_valid():
            formset.save()
            # Do something. Should generally end with a redirect. For example:
            return HttpResponseRedirect(gradingresult.get_absolute_url())
    else:
        formset = AssessmentUnitInlineFormSet(
            instance=gradingresult, form_kwargs={"request": request}
        )
    return render(request, "dashboard/gradingresult_form2.html", {"formset": formset})


@mfa_required
@permission_required("dashboard.change_gradingresult")
def manageGradingResultLetter(request, **kwargs):
    gradingresult = GradingResult.objects.get(pk=kwargs["pk"])
    AssessmentUnitInlineFormSet = inlineformset_factory(
        GradingResult,
        AssessmentUnit,
        form=AssessmentUnitLetterForm,
        extra=10 - gradingresult.assessmentunit_set.all().count(),
    )

    if request.method == "POST":
        formset = AssessmentUnitInlineFormSet(
            request.POST,
            request.FILES,
            instance=gradingresult,
            form_kwargs={"request": request},
        )
        if formset.is_valid():
            for form in formset:
                unit = form.cleaned_data.get("unit")
                if form.cleaned_data.get("unit"):
                    form.save()
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            # Do something. Should generally end with a redirect. For example:
            return HttpResponseRedirect(gradingresult.get_absolute_url())
    else:
        formset = AssessmentUnitInlineFormSet(
            instance=gradingresult, form_kwargs={"request", request}
        )
    return render(request, "dashboard/gradingresult_form2.html", {"formset": formset})


class ClassListView(MFARequiredMixin, LoginRequiredMixin, generic.ListView):
    model = Class

    def get_queryset(self):
        queryset = Class.objects.filter(
            type__style__pk=self.request.session.get("style", 1)
        ).all()

        # Process form data to filter queryset
        form = ClassSearchForm(self.request.GET, request=self.request)
        if form.is_valid():
            filters = {}

            # Iterate over form fields and add filters dynamically
            for field_name, value in form.cleaned_data.items():
                if value:
                    filters[field_name] = value

            # Apply all filters to the queryset in a single call
            queryset = queryset.filter(**filters)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = ClassSearchForm(self.request.GET, request=self.request)
        return context


class ClassDetailView(MFARequiredMixin, LoginRequiredMixin, generic.DetailView):
    model = Class

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ClassDetailView, self).get_context_data(**kwargs)
        cl = self.get_object()
        url = reverse("dash-batch-add-grading-invite") + "?"
        for student in cl.students.all():
            url += f"selected_items={student.pk}&"
        url = url.strip("&")
        context["batch_add_grading_invites_url"] = url
        return context


class ClassCreate(MFARequiredMixin, LoginRequiredMixin, CreateView):
    model = Class
    form_class = ClassForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class ClassUpdate(MFARequiredMixin, LoginRequiredMixin, UpdateView):
    model = Class
    form_class = ClassForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class ClassDelete(MFARequiredMixin, LoginRequiredMixin, DeleteView):
    model = Class
    success_url = reverse_lazy("dash-classes")


class PaymentListView(MFARequiredMixin, LoginRequiredMixin, generic.ListView):
    model = Payment

    def get_queryset(self):
        manager = Payment.objects

        # Process form data to filter queryset
        form = PaymentSearchForm(self.request.GET, request=self.request)
        if form.is_valid():
            filters = {}

            # Iterate over form fields and add filters dynamically
            for field_name, value in form.cleaned_data.items():
                if value:
                    if (
                        field_name != "selected_statuses"
                    ):  # we want to do this LAST because it requires loading all the objects rather than using a DB filter
                        filters[field_name] = value

            queryset_db = manager.filter(**filters).all()
            if form.cleaned_data.get("selected_statuses"):
                payment_list = [
                    payment
                    for payment in queryset_db
                    if payment.payment_status
                    in form.cleaned_data.get("selected_statuses")
                ]
                return manager.filter(
                    pk__in=[payment.pk for payment in payment_list]
                ).all()
            return queryset_db
        return manager.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = PaymentSearchForm(
            self.request.GET, request=self.request
        )
        return context


class PaymentDetailView(MFARequiredMixin, LoginRequiredMixin, generic.DetailView):
    model = Payment


class PaymentCreate(CreatePopupMixin, MFARequiredMixin, LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get("_popup", False)
        c["popup"] = popup
        return c

    def get_initial(self):
        # Autofill the member field based on the 'member' parameter in the URL
        member_id = self.request.GET.get("member")
        i = {}
        if member_id:
            i["member"] = member_id
        return i

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class PaymentUpdate(UpdatePopupMixin, MFARequiredMixin, LoginRequiredMixin, UpdateView):
    model = Payment
    form_class = PaymentForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get("_popup", False)
        c["popup"] = popup
        return c

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class PaymentDelete(MFARequiredMixin, LoginRequiredMixin, DeleteView):
    model = Payment
    success_url = reverse_lazy("dash-payments")


class GetStandardAmountView(MFARequiredMixin, LoginRequiredMixin, View):
    def get(self, request, pk):
        payment_type = get_object_or_404(PaymentType, pk=pk)
        standard_amount = payment_type.standard_amount
        return JsonResponse({"standard_amount": standard_amount})


class GetGradingInviteDetailView(MFARequiredMixin, LoginRequiredMixin, View):
    def get(self, request, pk):
        gradinginvite = get_object_or_404(GradingInvite, pk=pk)
        response = {
            "forbelt": gradinginvite.forbelt.pk,
            "gradingpk": gradinginvite.grading.pk,
        }
        return JsonResponse(response)


class MemberGetGradingInvites(MFARequiredMixin, LoginRequiredMixin, View):
    def get(self, request, pk):
        selected_member = get_object_or_404(Member, pk=pk)

        today = timezone.now().date()
        six_months_before = today - timedelta(days=6 * 30)

        grading_invites = (
            selected_member.gradinginvite_set.filter(
                grading__grading_datetime__date__gte=six_months_before
            )
            .filter(grading__grading_type__style=request.session.get("style", 1))
            .all()
        )

        data = [
            {"value": invite.id, "label": str(invite)} for invite in grading_invites
        ]
        return JsonResponse(data, safe=False)


class GetGradingsJSON(MFARequiredMixin, LoginRequiredMixin, View):
    def get(self, request):
        gradings = Grading.objects.filter(
            grading_type__style__pk=self.request.session.get("style", 1)
        ).all()
        data = [{"value": grading.id, "label": str(grading)} for grading in gradings]
        return JsonResponse(data, safe=False)


class MemberGetPayments(MFARequiredMixin, LoginRequiredMixin, View):
    def get(self, request, pk):
        selected_member = get_object_or_404(Member, pk=pk)

        today = timezone.now().date()
        six_months_before = today - timedelta(days=6 * 30)

        payments = (
            selected_member.payment_set.filter(date_created__gte=six_months_before)
            .all()
            .order_by("-date_created")
        )

        data = [{"value": payment.id, "label": str(payment)} for payment in payments]
        return JsonResponse(data, safe=False)


class MemberGetDetails(MFARequiredMixin, LoginRequiredMixin, View):
    def get(self, request, pk):
        selected_member = get_object_or_404(Member, pk=pk)
        data = model_to_dict(selected_member)
        style = request.session.get("style", 1)
        data["belt"] = data["belts"].filter(style__pk=style)
        data["next_belt"] = get_object_or_404(
            Belt, style=style, degree=(data.get("belt").degree + 1)
        ).pk
        data["belt"] = data["belt"].pk
        return JsonResponse(data, safe=False)


class GradingInviteDetailView(MFARequiredMixin, LoginRequiredMixin, generic.DetailView):
    model = GradingInvite


class GradingInviteListView(MFARequiredMixin, LoginRequiredMixin, generic.ListView):
    model = GradingInvite

    def get_queryset(self):
        queryset = GradingInvite.objects.filter(
            grading__grading_type__style__pk=self.request.session.get("style", 1)
        ).all()

        # Process form data to filter queryset
        form = GradingInviteSearchForm(self.request.GET, request=self.request)
        if form.is_valid():
            filters = {}

            # Iterate over form fields and add filters dynamically
            for field_name, value in form.cleaned_data.items():
                if field_name == "date" and value:
                    filters["grading__grading_datetime__date"] = value
                elif field_name == "type" and value:
                    filters["grading__grading_type"] = value
                else:
                    if value:
                        filters[field_name] = value

            # Apply all filters to the queryset in a single call
            queryset = queryset.filter(**filters)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = GradingInviteSearchForm(
            self.request.GET, request=self.request
        )
        # get initial values for the checkboxes
        selected_pks = self.request.GET.getlist("selected_items")
        pks = [int(pk) for pk in selected_pks]
        gradinginviteobjectlist = list(context["gradinginvite_list"].iterator())
        selected = []
        for giobj in gradinginviteobjectlist:
            selected.append(giobj.pk in pks)
        context["uselist"] = zip(selected, gradinginviteobjectlist)
        return context


class GradingInviteDelete(MFARequiredMixin, LoginRequiredMixin, DeleteView):
    model = GradingInvite
    success_url = reverse_lazy("dash-gradinginvites")


class GradingInviteCreate(
    CreatePopupMixin, MFARequiredMixin, LoginRequiredMixin, CreateView
):
    model = GradingInvite
    form_class = GradingInviteForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get("_popup", False)
        c["popup"] = popup
        return c

    def get_initial(self):
        # Autofill the member field based on the 'member_id' parameter in the URL
        member_id = self.request.GET.get("member")
        grading = self.request.GET.get("grading")
        forbelt = self.request.GET.get("forbelt")

        i = {}
        if member_id:
            i["member"] = member_id

        if forbelt:
            i["forbelt"] = get_object_or_404(Belt, pk=forbelt)
        elif member_id:
            i["forbelt"] = get_object_or_404(
                Belt, pk=(int(Member.objects.get(id=member_id).belt.pk) + 1)
            )

        if grading:
            i["grading"] = grading

        return i

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class GradingInviteUpdate(
    UpdatePopupMixin, MFARequiredMixin, LoginRequiredMixin, UpdateView
):
    model = GradingInvite
    form_class = GradingInviteForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get("_popup", False)
        c["popup"] = popup
        return c


@login_required
@mfa_required
def gradinginvite_pdf_view(request, pk, **kwargs):
    gi = get_object_or_404(GradingInvite, pk=pk)
    data = {"gradinginvite": gi}
    return renderers.PDFResponse(
        "dashboard/gradinginvite_pdf.html",
        f'GradingInvitation_{gi.member.first_name}{gi.member.last_name}_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf',
        data,
    )


class GradingDetailView(MFARequiredMixin, LoginRequiredMixin, generic.DetailView):
    model = Grading


class GradingListView(MFARequiredMixin, LoginRequiredMixin, generic.ListView):
    model = Grading

    def get_queryset(self):
        queryset = Grading.objects.filter(
            grading_type__style__pk=self.request.session.get("style", 1)
        ).all()
        return queryset


class GradingDelete(MFARequiredMixin, LoginRequiredMixin, DeleteView):
    model = Grading
    success_url = reverse_lazy("dash-gradings")


class GradingCreate(CreatePopupMixin, MFARequiredMixin, LoginRequiredMixin, CreateView):
    model = Grading
    form_class = GradingForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get("_popup", False)
        c["popup"] = popup
        return c

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class GradingUpdate(UpdatePopupMixin, MFARequiredMixin, LoginRequiredMixin, UpdateView):
    model = Grading
    form_class = GradingForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get("_popup", False)
        c["popup"] = popup
        return c

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


@login_required
@mfa_required
def gradingresult_pdf_view(request, pk, **kwargs):
    gr = get_object_or_404(GradingResult, pk=pk)
    data = {"gradingresult": gr}
    assessmentunits = gr.assessmentunit_set.all()
    if assessmentunits:
        maxpts = 0
        apts = 0
        for au in assessmentunits:
            maxpts += au.max_pts
            apts += au.achieved_pts
        if gr.is_letter:
            data["average_grade"] = LETTER_GRADES[round(apts / (len(assessmentunits)))]
        else:
            data["total_max_pts"] = maxpts
            data["total_achieved_pts"] = apts
            data["total_percent"] = round(
                (data["total_achieved_pts"] / data["total_max_pts"]) * 100
            )
    return renderers.PDFResponse(
        "dashboard/gradingresult_pdf.html",
        f'GradingResult_{gr.member.first_name}{gr.member.last_name}_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf',
        data,
    )


@login_required
@mfa_required
def gradingresult_batch_pdf_view(request, **kwargs):
    pks = request.GET.getlist("selected_items")
    if pks:
        merger = PdfWriter()
        buffer = BytesIO()
        for pk in pks:
            gr = get_object_or_404(GradingResult, pk=pk)
            data = {"gradingresult": gr}
            assessmentunits = gr.assessmentunit_set.all()
            if assessmentunits:
                maxpts = 0
                apts = 0
                for au in assessmentunits:
                    maxpts += au.max_pts
                    apts += au.achieved_pts
                if gr.is_letter:
                    data["average_grade"] = LETTER_GRADES[
                        round(apts / (len(assessmentunits)))
                    ]
                else:
                    data["total_max_pts"] = maxpts
                    data["total_achieved_pts"] = apts
                    data["total_percent"] = round(
                        (data["total_achieved_pts"] / data["total_max_pts"]) * 100
                    )
            merger.append(
                PdfReader(
                    renderers.render_to_pdf("dashboard/gradingresult_pdf.html", data)
                )
            )
        merger.write(buffer)
        merger.close()

        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="GradingResults_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf"'
        )
        return response
    else:
        return HttpResponse(status=204)


@login_required
@mfa_required
def gradinginvite_batch_pdf_view(request, **kwargs):
    pks = request.GET.getlist("selected_items")
    if pks:
        merger = PdfWriter()
        buffer = BytesIO()
        for pk in pks:
            gi = get_object_or_404(GradingInvite, pk=pk)
            data = {"gradinginvite": gi}
            merger.append(
                PdfReader(
                    renderers.render_to_pdf("dashboard/gradinginvite_pdf.html", data)
                )
            )
        merger.write(buffer)
        merger.close()

        response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = (
            f'attachment; filename="GradingInvites_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf"'
        )
        return response
    else:
        return HttpResponse(status=204)


@mfa_required
@permission_required("dashboard.add_gradingresult")
def gradinginvite_batch_create(request, **kwargs):
    GradingInviteFormSet = modelformset_factory(
        GradingInvite, form=GradingInviteBulkForm, extra=0
    )

    if request.method == "POST":
        formset = GradingInviteFormSet(
            request.POST, request.FILES, prefix="gradinginvites"
        )
        gradingselectform = GradingSelectForm(prefix="miscselect")
        if formset.is_valid():
            # ADD ISSUED_BY AND CREATE/ADD PAYMENTS
            gi_pks = []
            for form in formset:
                if form.cleaned_data["select"]:
                    gi = form.save(commit=False)
                    gi.issued_by = request.user
                    pt = 12
                    p = Payment(
                        member=form.cleaned_data["member"],
                        paymenttype=get_object_or_404(PaymentType, pk=pt),
                        amount_due=get_object_or_404(
                            PaymentType, pk=pt
                        ).standard_amount,
                    )
                    p.save()
                    gi.payment = p
                    gi.save()
                    gi_pks.append(gi.pk)

            instances = formset.save(commit=False)
            qd = QueryDict(mutable=True)
            for pk in gi_pks:
                qd.update({"selected_items": pk})
            return HttpResponseRedirect(
                reverse("dash-batch-revise-grading-invite") + "?" + qd.urlencode()
            )
    else:
        # GET request
        pks = request.GET.getlist("selected_items")
        GradingInviteFormSet = modelformset_factory(
            GradingInvite, form=GradingInviteBulkForm, extra=len(pks)
        )
        formset = GradingInviteFormSet(
            initial=[
                {
                    "member": pk,
                    "forbelt": get_object_or_404(
                        Belt, pk=(get_object_or_404(Member, pk=pk).belt.pk + 1)
                    ),
                }
                for pk in pks
            ],
            queryset=GradingInvite.objects.none(),
            prefix="gradinginvites",
            form_kwargs={"request", request},
        )
        gradingselectform = GradingSelectForm(prefix="miscselect", request=request)
    return render(
        request,
        "dashboard/gradinginvite_batch_create.html",
        {"formset": formset, "miscform": gradingselectform},
    )


@mfa_required
@permission_required("dashboard.add_belt")
def manageBelts(request, **kwargs):
    BeltFormSet = modelformset_factory(
        Belt,
        form=BeltForm,
        formset=ConvenientBaseModelFormSet,
        extra=0,
        can_delete=True,
        can_order=True,
    )

    if request.method == "POST":
        formset = BeltFormSet(request.POST, request.FILES, prefix="belt-formset")
        if formset.is_valid():
            with transaction.atomic():
                no_forms = len(formset)
                for i, form in enumerate(formset.ordered_forms):
                    belt = form.save(commit=False)
                    belt.degree = no_forms - i
                    belt.style = get_object_or_404(
                        Style, pk=request.session.get("style", 1)
                    )
                    belt.save()
                instances = formset.save(commit=False)
                for obj in formset.deleted_objects:
                    obj.delete()
    else:
        formset = BeltFormSet(
            prefix="belt-formset",
            queryset=Belt.objects.filter(style__pk=request.session.get("style", 1)),
        )
    return render(request, "dashboard/manage_belts.html", {"formset": formset})


@login_required
@mfa_required
def batch_gradinginvite_revise(request, **kwargs):
    pks = request.GET.getlist("selected_items")
    gis = [get_object_or_404(GradingInvite, pk=pk) for pk in pks]

    url = reverse("dash-gradinginvites") + "?"
    for pk in pks:
        url += f"selected_items={pk}&"
    url = url.strip("&")
    return render(
        request,
        "dashboard/gradinginvite_batch_revise.html",
        {"gradinginvites": gis, "grading_invites_url": url},
    )


@login_required
@mfa_required
def gradingresult_batch_email_view(request, **kwargs):
    """
    View that sends emails with the GR PDF attached to the email the assessed member has on file
    GRs to be sent are specified by the selected_items query key
    """
    try:
        pks = request.GET.getlist("selected_items")
    except:
        response_data = {
            "success": False,
            "message": "No items selected for email sending.",
        }
        return JsonResponse(response_data, status=204)
    if pks:
        messages = []
        for pk in pks:
            gr = get_object_or_404(GradingResult, pk=pk)
            data = {"gradingresult": gr}
            assessmentunits = gr.assessmentunit_set.all()
            if assessmentunits:
                maxpts = 0
                apts = 0
                for au in assessmentunits:
                    maxpts += au.max_pts
                    apts += au.achieved_pts
                if gr.is_letter:
                    data["average_grade"] = LETTER_GRADES[
                        round(apts / (len(assessmentunits)))
                    ]
                else:
                    data["total_max_pts"] = maxpts
                    data["total_achieved_pts"] = apts
                    data["total_percent"] = round(
                        (data["total_achieved_pts"] / data["total_max_pts"]) * 100
                    )
            message = mail.EmailMessage(
                f"Grading Certificate for {gr.member}",
                "Please see attached your Grading Certificate.\n - TKD Manager.",
                "beaniemcc1@gmail.com",
                (f"{gr.member.email}",),
                attachments=[
                    (
                        f'GradingResult_{gr.member.first_name}{gr.member.last_name}_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf',
                        renderers.render_to_pdf(
                            "dashboard/gradingresult_pdf.html", data
                        ).getvalue(),
                        "application/pdf",
                    )
                ],
            )
            messages.append(message)
        connection = mail.get_connection()  # Use default email connection
        connection.send_messages(messages)
        response_data = {"success": True, "message": "Emails sent successfully!"}
        return JsonResponse(response_data)
    else:
        response_data = {
            "success": False,
            "message": "No items selected for email sending.",
        }
        return JsonResponse(response_data, status=204)


@login_required
@mfa_required
def gradinginvite_batch_email_view(request, **kwargs):
    """
    View that sends emails with the GI PDF attached to the email the assessed member has on file
    GIs to be sent are specified by the selected_items query key
    """
    try:
        pks = request.GET.getlist("selected_items")
    except:
        response_data = {
            "success": False,
            "message": "No items selected for email sending.",
        }
        return JsonResponse(response_data, status=204)
    if pks:
        messages = []
        for pk in pks:
            gi = get_object_or_404(GradingInvite, pk=pk)
            data = {"gradinginvite": gi}
            # renderers.PDFResponse('dashboard/gradinginvite_pdf.html', f'GradingInvitation_{gi.member.first_name}{gi.member.last_name}_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf', data)
            message = mail.EmailMessage(
                f"Grading Invite for {gi.member}",
                "Please see attached your Grading Invite.\n - TKD Manager.",
                "beaniemcc1@gmail.com",
                (f"{gi.member.email}",),
                attachments=[
                    (
                        f'GradingInvitation_{gi.member.first_name}{gi.member.last_name}_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf',
                        renderers.render_to_pdf(
                            "dashboard/gradinginvite_pdf.html", data
                        ).getvalue(),
                        "application/pdf",
                    )
                ],
            )
            messages.append(message)
        connection = mail.get_connection()  # Use default email connection
        connection.send_messages(messages)
        response_data = {"success": True, "message": "Emails sent successfully!"}
        return JsonResponse(response_data)
    else:
        response_data = {
            "success": False,
            "message": "No items selected for email sending.",
        }
        return JsonResponse(response_data, status=204)


class RecurringPaymentDetailView(
    MFARequiredMixin, LoginRequiredMixin, generic.DetailView
):
    model = RecurringPayment


class RecurringPaymentListView(MFARequiredMixin, LoginRequiredMixin, generic.ListView):
    model = RecurringPayment

    def get_queryset(self):
        manager = RecurringPayment.objects

        # Process form data to filter queryset
        form = RecurringPaymentSearchForm(self.request.GET, request=self.request)
        if form.is_valid():
            filters = {}

            # Iterate over form fields and add filters dynamically
            for field_name, value in form.cleaned_data.items():
                if value:
                    filters[field_name] = value

            queryset_db = manager.filter(**filters).all()
            return queryset_db
        return manager.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_form"] = RecurringPaymentSearchForm(
            self.request.GET, request=self.request
        )
        return context


class RecurringPaymentCreate(MFARequiredMixin, LoginRequiredMixin, CreateView):
    model = RecurringPayment
    form_class = RecurringPaymentForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class RecurringPaymentUpdate(MFARequiredMixin, LoginRequiredMixin, UpdateView):
    model = RecurringPayment
    form_class = RecurringPaymentUpdateForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs


class RecurringPaymentDelete(MFARequiredMixin, LoginRequiredMixin, DeleteView):
    model = RecurringPayment
    success_url = reverse_lazy("dash-rpayments")


class PaymentTypeCreate(
    CreatePopupMixin, MFARequiredMixin, LoginRequiredMixin, CreateView
):
    model = PaymentType
    form_class = PaymentTypeForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get("_popup", False)
        c["popup"] = popup
        return c


class PaymentTypeUpdate(
    UpdatePopupMixin, MFARequiredMixin, LoginRequiredMixin, UpdateView
):
    model = PaymentType
    form_class = PaymentTypeForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get("_popup", False)
        c["popup"] = popup
        return c


class PaymentTypeDelete(MFARequiredMixin, LoginRequiredMixin, DeleteView):
    model = PaymentType
    success_url = reverse_lazy("dash-payment-types")


class PaymentTypeDetailView(MFARequiredMixin, LoginRequiredMixin, generic.DetailView):
    model = PaymentType


class PaymentTypeListView(MFARequiredMixin, LoginRequiredMixin, generic.ListView):
    model = PaymentType


def selectStyle(request, pk):
    request.session["style"] = pk
    return HttpResponse()


@mfa_required
@permission_required("dashboard.add_style")
def manageStyles(request, **kwargs):
    StyleFormSet = modelformset_factory(
        Style, form=StyleForm, formset=ConvenientBaseModelFormSet, can_delete=True
    )

    if request.method == "POST":
        formset = StyleFormSet(request.POST, request.FILES, prefix="style-formset")
        if formset.is_valid():
            formset.save()
    else:
        formset = StyleFormSet(prefix="style-formset", queryset=Style.objects.all())
    return render(request, "dashboard/manage_styles.html", {"formset": formset})


@mfa_required
@permission_required("dashboard.add_assessmentunittype")
def manageAssessmentUnitTypes(request, **kwargs):
    AssessmentUnitTypeFormSet = modelformset_factory(
        AssessmentUnitType,
        form=AssessmentUnitTypeForm,
        formset=ConvenientBaseModelFormSet,
        can_delete=True,
    )

    if request.method == "POST":
        formset = AssessmentUnitTypeFormSet(
            request.POST, request.FILES, prefix="assessmentunittype-formset"
        )
        if formset.is_valid():
            for form in formset.forms:
                aut = form.save(commit=False)
                aut.style = get_object_or_404(Style, request.session.get("style", 1))
                aut.save()
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
    else:
        formset = AssessmentUnitTypeFormSet(
            prefix="assessmentunittype-formset",
            queryset=AssessmentUnitType.objects.filter(
                style__pk=request.session.get("style", 1)
            ),
        )
    return render(
        request, "dashboard/manage_assessmentunittypes.html", {"formset": formset}
    )


@mfa_required
@permission_required(["dashboard.add_classtype", "dashboard.add_gradingtype"])
def manageClassTypeGradingType(request):
    ClassTypeFormSet = modelformset_factory(
        ClassType,
        form=ClassTypeForm,
        formset=ConvenientBaseModelFormSet,
        can_delete=True,
    )
    GradingTypeFormSet = modelformset_factory(
        GradingType,
        form=GradingTypeForm,
        formset=ConvenientBaseModelFormSet,
        can_delete=True,
    )

    if request.method == "POST":
        classtype_formset = ClassTypeFormSet(
            request.POST, request.FILES, prefix="classtype-formset"
        )
        gradingtype_formset = ClassTypeFormSet(
            request.POST, request.FILES, prefix="gradingtype-formset"
        )
        if gradingtype_formset.is_valid() and classtype_formset.is_valid():
            for form in gradingtype_formset.forms:
                gt = form.save(commit=False)
                gt.style = get_object_or_404(Style, request.session.get("style", 1))
                gt.save()
            instances = gradingtype_formset.save(commit=False)
            for obj in gradingtype_formset.deleted_objects:
                obj.delete()
            for form in classtype_formset.forms:
                ct = form.save(commit=False)
                ct.style = get_object_or_404(Style, request.session.get("style", 1))
                ct.save()
            instances = classtype_formset.save(commit=False)
            for obj in classtype_formset.deleted_objects:
                obj.delete()
    else:
        classtype_formset = ClassTypeFormSet(
            prefix="classtype-formset",
            queryset=ClassType.objects.filter(
                style__pk=request.session.get("style", 1)
            ),
        )
        gradingtype_formset = GradingTypeFormSet(
            prefix="gradingtype-formset",
            queryset=GradingType.objects.filter(
                style__pk=request.session.get("style", 1)
            ),
        )
    return render(
        request,
        "dashboard/manage_classtypesgradingtypes.html",
        {
            "gradingtype_formset": gradingtype_formset,
            "classtype_formset": classtype_formset,
        },
    )


@mfa_required
@permission_required(
    ["dashboard.add_memberproperty", "dashboard.add_memberpropertytype"]
)
def manageMemberPropertyMemberPropertyType(request):
    StyleMPTswithMPsFormset = inlineformset_factory(
        Style,
        MemberPropertyType,
        formset=BaseMPTsWithMPsFormset,
        # We need to specify at least one MPT field:
        fields=("name", "searchable", "teacher_property"),
        extra=1,
        # If you don't want to be able to delete Styles:
        can_delete=False,
    )
    if request.method == "POST":
        formset = StyleMPTswithMPsFormset(request.POST, request.FILES)
        with transaction.atomic():
            formset.save()
    else:
        # make a mpt formset with a prefix, and then make a bunch of memberproperty formsets (one for each mpt with a prefix)
        formset = StyleMPTswithMPsFormset(
            instance=Style.objects.get(pk=request.session.get("style", 1))
        )

    return render(
        request,
        "dashboard/manage_memberpropertymemberpropertytype.html",
        {"formset": formset},
    )


@mfa_required
@permission_required(
    ["dashboard.add_memberproperty", "dashboard.add_memberpropertytype"]
)
def manageMemberPropertyMemberPropertyTypeunstyled(request):
    StyleMPTswithMPsFormset = inlineformset_factory(
        Style,
        MemberPropertyType,
        formset=BaseMPTsWithMPsFormset,
        # We need to specify at least one MPT field:
        fields=("name", "searchable", "teacher_property"),
        extra=1,
        # If you don't want to be able to delete Styles:
        can_delete=False,
    )
    if request.method == "POST":
        formset = StyleMPTswithMPsFormset(request.POST, request.FILES)
        with transaction.atomic():
            formset.save()
    else:
        # make a mpt formset with a prefix, and then make a bunch of memberproperty formsets (one for each mpt with a prefix)
        formset = StyleMPTswithMPsFormset(instance=None)

    return render(
        request,
        "dashboard/manage_memberpropertymemberpropertytype.html",
        {"formset": formset},
    )
