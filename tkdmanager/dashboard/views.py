from datetime import date, datetime, timedelta
from io import BytesIO
from typing import Any
from convenient_formsets import ConvenientBaseModelFormSet

from dashboard import renderers
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.core import mail
from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms import (BooleanField, Form, ModelChoiceField, ModelForm,
                          inlineformset_factory, modelformset_factory)
from django.forms.models import model_to_dict
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
                         QueryDict)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views import View, generic
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from pypdf import PdfReader, PdfWriter
from rest_framework.authtoken.models import Token

from .forms import *
from .models import (GRADINGS, LETTER_GRADES, AssessmentUnit, Award, Class,
                     Grading, GradingInvite, GradingResult, Member, Payment,
                     PaymentType, RecurringPayment, Belt, AssessmentUnitType)


def time_difference_in_seconds(time1, time2):
    # Convert time objects to timedelta
    delta = datetime.combine(timezone.now().date(), time2) - datetime.combine(timezone.now().date(), time1)
    # Calculate the time difference in seconds
    difference_seconds = delta.total_seconds()
    return difference_seconds

# Create your views here.
@login_required
def index(request):
    """homepage"""

    # Number of members
    num_members = Member.objects.count()
    num_active_members = Member.objects.filter(active__exact=True).count()
    belts = Belt.objects.all()
    labels = [belt.name for belt in belts]
    counts = [belt.member_set.count() for belt in belts]

    context = {
        'num_members': num_members,
        'num_active_members': num_active_members,
        'belt_labels': labels,
        'belt_count': counts,
    }

    return render(request, 'home.html', context=context)

@permission_required('authtoken.add_token')
def token_display(request):
    token, created = Token.objects.get_or_create(user=request.user)
    context = {
        'token': token.key
    }

    return render(request, 'token.html', context=context)

@permission_required('authtoken.delete_token')
def token_delete(request):
    token = get_object_or_404(Token, user=request.user)
    token.delete()
    return HttpResponseRedirect(reverse_lazy('dash-get-token'))

def health(request):
    return JsonResponse({'STATUS': 'OK', 'TIMESTAMP': timezone.now()})

class MemberListView(LoginRequiredMixin, generic.ListView):
    model = Member
    ordering = ['-belt','last_name']

    def get_queryset(self):
        queryset = Member.objects.all()

        # Process form data to filter queryset
        form = MemberSearchForm(self.request.GET)
        if form.is_valid():
            filters = {}

            # Iterate over form fields and add filters dynamically
            for field_name, value in form.cleaned_data.items():
                if field_name == 'member' and value:
                    queryset = Member.objects.filter(pk=value.pk).all()
                    return queryset
                if value:
                    filters[field_name] = value
            
            # Apply all filters to the queryset in a single call
            queryset = queryset.filter(**filters)

        return queryset
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = MemberSearchForm(self.request.GET)
        return context

class MemberDetailView(LoginRequiredMixin, generic.DetailView):
    model = Member

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(MemberDetailView, self).get_context_data(**kwargs)
        
        # Find no. hours taught
        classes_taught = self.get_object().instructors2classes.all()

        # Use sum with a generator expression to calculate total seconds
        total_seconds = sum(time_difference_in_seconds(cl.start, cl.end) for cl in classes_taught)

        # Calculate hours directly from total seconds
        hours = round(total_seconds / 3600, 2)

        context['hours_taught'] = hours

        # Find overdue payments + those for the next 6 months
        today = timezone.now().date()
        six_months_later = today + timedelta(days=6 * 30)
        six_months_before = today - timedelta(days=6 * 30)
        recent_payments = self.get_object().payment_set.filter(Q(date_due__date__gte=six_months_before) & Q(date_due__date__lte=six_months_later)).all()
        payments = self.get_object().payment_set.all()
        overdue_payments = [p for p in payments if p.payment_status == "Overdue"]
        context['relevant_payments'] = list(recent_payments) + overdue_payments
        return context

class GradingResultDetailView(LoginRequiredMixin, generic.DetailView):
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
                context['average_grade'] = LETTER_GRADES[round(apts/(len(assessmentunits)))]
            else:
                context['total_max_pts'] = maxpts
                context['total_achieved_pts'] = apts
                context['total_percent'] = round((context['total_achieved_pts']/context['total_max_pts'])*100)
            
        return context
    
class GradingResultListView(LoginRequiredMixin, generic.ListView):
    model = GradingResult

    def get_queryset(self):
        queryset = GradingResult.objects.filter(style__pk=self.request.session.get('pk', 1)).all()

        # Process form data to filter queryset
        form = GradingResultSearchForm(self.request.GET)
        if form.is_valid():
            filters = {}

            # Iterate over form fields and add filters dynamically
            for field_name, value in form.cleaned_data.items():
                if field_name == 'date' and value:
                    filters['grading__grading_datetime__date'] = value
                elif field_name == 'type' and value:
                    filters['grading__grading_type__exact'] = value
                else:
                    if value:
                        filters[field_name] = value
            
            # Apply all filters to the queryset in a single call
            queryset = queryset.filter(**filters)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = GradingResultSearchForm(self.request.GET)
        return context
    
class MemberCreate(LoginRequiredMixin, CreateView):
    model = Member
    form_class = MemberForm

class MemberUpdate(LoginRequiredMixin, UpdateView):
    model = Member
    form_class = MemberForm

class MemberDelete(LoginRequiredMixin, DeleteView):
    model = Member
    success_url = reverse_lazy("dash-members")

class GradingResultCreate(LoginRequiredMixin, CreateView):
    form_class = GradingResultCreateForm
    model = GradingResult
    template_name = 'dashboard/gradingresult_form.html'

    def form_valid(self, form):
        response = super(GradingResultCreate, self).form_valid(form)
        # do something with self.object
        target = self.object.member
        target.belt = target.member2gradings.order_by('-grading__grading_datetime').first().forbelt
        target.save()
        return response

    def get_success_url(self):
        if self.object.is_letter:
            return reverse('dash-update-grading-result3', kwargs={'pk':self.object.pk})
        else:
            return reverse('dash-update-grading-result2', kwargs={'pk':self.object.pk})
    
    def get_initial(self):
        # Autofill the member field based on the 'member_id' parameter in the URL
        member_id = self.request.GET.get('member_id')
        i = {}
        if member_id:
            i['member'] = member_id
            i['forbelt'] = get_object_or_404(Belt, pk=(Member.objects.get(id=member_id).belt.pk + 1))
        return i

class GradingResultUpdate(LoginRequiredMixin, UpdateView):
    form_class = GradingResultUpdateForm
    template_name = 'dashboard/gradingresult_form.html'
    model = GradingResult

    def form_valid(self, form):
        response = super(GradingResultUpdate, self).form_valid(form)
        # do something with self.object
        target = self.object.member
        target.belt = target.member2gradings.order_by('-grading__grading_datetime').first().forbelt
        target.save()
        return response
    
    def get_success_url(self):
        if self.object.is_letter:
            return reverse('dash-update-grading-result3', kwargs={'pk':self.object.pk})
        else:
            return reverse('dash-update-grading-result2', kwargs={'pk':self.object.pk})

class GradingResultDelete(LoginRequiredMixin, DeleteView):
    model = GradingResult
    success_url = reverse_lazy("dash-gradingresults")

class AwardListView(LoginRequiredMixin, generic.ListView):
    model = Award

    def get_queryset(self):
        queryset = Award.objects.filter(style__pk=self.request.session.get('pk', 1)).all()
        return queryset

class AwardCreate(CreatePopupMixin, LoginRequiredMixin, CreateView):
    model = Award
    fields = ['name']

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get('_popup', False)
        c['popup'] = popup
        return c

class AwardUpdate(UpdatePopupMixin, LoginRequiredMixin, UpdateView):
    model = Award
    fields = ['name']

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get('_popup', False)
        c['popup'] = popup
        return c

class AwardDelete(LoginRequiredMixin, DeleteView):
    model = Award
    success_url = reverse_lazy("dash-awards")

class AwardDetailView(LoginRequiredMixin, generic.DetailView):
    model = Award
        
@permission_required("dashboard.change_gradingresult")
def manageGradingResult(request, **kwargs):
    gradingresult = GradingResult.objects.get(pk=kwargs['pk'])
    AssessmentUnitInlineFormSet = inlineformset_factory(GradingResult, AssessmentUnit, form=AssessmentUnitGradingResultForm, extra=10-gradingresult.assessmentunit_set.all().count())
    
    if request.method == "POST":
        formset = AssessmentUnitInlineFormSet(request.POST, request.FILES, instance=gradingresult, form_kwargs={'request': request})
        if formset.is_valid():
            formset.save()
            # Do something. Should generally end with a redirect. For example:
            return HttpResponseRedirect(gradingresult.get_absolute_url())
    else:
        formset = AssessmentUnitInlineFormSet(instance=gradingresult, form_kwargs={'request': request})
    return render(request, 'dashboard/gradingresult_form2.html', {'formset': formset})

@permission_required("dashboard.change_gradingresult")
def manageGradingResultLetter(request, **kwargs):
    gradingresult = GradingResult.objects.get(pk=kwargs['pk'])
    AssessmentUnitInlineFormSet = inlineformset_factory(GradingResult, AssessmentUnit, form=AssessmentUnitLetterForm, extra=10-gradingresult.assessmentunit_set.all().count())
    
    if request.method == "POST":
        formset = AssessmentUnitInlineFormSet(request.POST, request.FILES, instance=gradingresult, form_kwargs={'request': request})
        if formset.is_valid():
            for form in formset:
                unit = form.cleaned_data.get('unit')
                if form.cleaned_data.get('unit'):
                    form.save()
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                obj.delete()
            # Do something. Should generally end with a redirect. For example:
            return HttpResponseRedirect(gradingresult.get_absolute_url())
    else:
        formset = AssessmentUnitInlineFormSet(instance=gradingresult, form_kwargs={'request', request})
    return render(request, 'dashboard/gradingresult_form2.html', {'formset': formset})    

class ClassListView(LoginRequiredMixin, generic.ListView):
    model = Class

    def get_queryset(self):
        queryset = Class.objects.filter(classtype__style__pk=self.request.session.get('pk', 1)).all()

        # Process form data to filter queryset
        form = ClassSearchForm(self.request.GET)
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
        context['search_form'] = ClassSearchForm(self.request.GET)
        return context         
        
class ClassDetailView(LoginRequiredMixin, generic.DetailView):
    model = Class

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ClassDetailView, self).get_context_data(**kwargs)
        cl = self.get_object()
        url = reverse('dash-batch-add-grading-invite')+'?'
        for student in cl.students.all():
            url += (f'selected_items={student.pk}&')
        url = url.strip('&')
        context['batch_add_grading_invites_url'] = url
        return context

class ClassCreate(LoginRequiredMixin, CreateView):
    model = Class
    form_class = ClassForm

class ClassUpdate(LoginRequiredMixin, UpdateView):
    model = Class
    form_class = ClassForm

class ClassDelete(LoginRequiredMixin, DeleteView):
    model = Class
    success_url = reverse_lazy("dash-classes")

class PaymentListView(LoginRequiredMixin, generic.ListView):
    model = Payment

    def get_queryset(self):
        manager = Payment.objects

        # Process form data to filter queryset
        form = PaymentSearchForm(self.request.GET)
        if form.is_valid():
            filters = {}

            # Iterate over form fields and add filters dynamically
            for field_name, value in form.cleaned_data.items():
                if value:
                    if field_name != "selected_statuses": # we want to do this LAST because it requires loading all the objects rather than using a DB filter
                        filters[field_name] = value

            queryset_db = manager.filter(**filters).all()
            if form.cleaned_data.get("selected_statuses"):
                payment_list = [payment for payment in queryset_db if payment.payment_status in form.cleaned_data.get("selected_statuses")]
                return manager.filter(pk__in=[payment.pk for payment in payment_list]).all()
            return queryset_db
        return manager.all()
            
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PaymentSearchForm(self.request.GET)
        return context  

class PaymentDetailView(LoginRequiredMixin, generic.DetailView):
    model = Payment

class PaymentCreate(CreatePopupMixin, LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get('_popup', False)
        c['popup'] = popup
        return c
    
    def get_initial(self):
        # Autofill the member field based on the 'member' parameter in the URL
        member_id = self.request.GET.get('member')
        i = {}
        if member_id:
            i['member'] = member_id
        return i

class PaymentUpdate(UpdatePopupMixin, LoginRequiredMixin, UpdateView):
    model = Payment
    form_class = PaymentForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get('_popup', False)
        c['popup'] = popup
        return c

class PaymentDelete(LoginRequiredMixin, DeleteView):
    model = Payment
    success_url = reverse_lazy("dash-payments")

class GetStandardAmountView(LoginRequiredMixin, View):
    def get(self, request, pk):
        payment_type = get_object_or_404(PaymentType, pk=pk)
        standard_amount = payment_type.standard_amount
        return JsonResponse({'standard_amount': standard_amount})

class GetGradingInviteDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        gradinginvite = get_object_or_404(GradingInvite, pk=pk)
        response = {
            'forbelt': gradinginvite.forbelt.pk,
            'gradingpk': gradinginvite.grading.pk,
        }
        return JsonResponse(response)
    
class MemberGetGradingInvites(LoginRequiredMixin, View):
    def get(self, request, pk):
        selected_member = get_object_or_404(Member, pk=pk)

        today = timezone.now().date()
        six_months_before = today - timedelta(days=6 * 30)

        grading_invites = selected_member.gradinginvite_set.filter(grading__grading_datetime__date__gte=six_months_before).all()

        data = [{'value': invite.id, 'label': str(invite)} for invite in grading_invites]
        return JsonResponse(data, safe=False)

class GetGradingsJSON(LoginRequiredMixin, View):
    def get(self, request):
        gradings = Grading.objects.all()
        data = [{'value': grading.id, 'label': str(grading)} for grading in gradings]
        return JsonResponse(data, safe=False)

class MemberGetPayments(LoginRequiredMixin, View):
    def get(self, request, pk):
        selected_member = get_object_or_404(Member, pk=pk)

        today = timezone.now().date()
        six_months_before = today - timedelta(days=6 * 30)

        payments = selected_member.payment_set.filter(date_created__gte=six_months_before).all().order_by("-date_created")

        data = [{'value': payment.id, 'label': str(payment)} for payment in payments]
        return JsonResponse(data, safe=False)
    
class MemberGetDetails(LoginRequiredMixin, View):
    def get(self, request, pk):
        selected_member = get_object_or_404(Member, pk=pk)
        data = model_to_dict(selected_member)
        data['next_belt'] = get_object_or_404(Belt, degree=(data.get('belt').degree + 1)).pk
        data['belt'] = data['belt'].pk
        return JsonResponse(data, safe=False)

class GradingInviteDetailView(LoginRequiredMixin, generic.DetailView):
    model = GradingInvite

class GradingInviteListView(LoginRequiredMixin, generic.ListView):
    model = GradingInvite

    def get_queryset(self):
        queryset = GradingInvite.objects.filter(style__pk=self.request.session.get('pk', 1)).all()

        # Process form data to filter queryset
        form = GradingInviteSearchForm(self.request.GET)
        if form.is_valid():
            filters = {}

            # Iterate over form fields and add filters dynamically
            for field_name, value in form.cleaned_data.items():
                if field_name == 'date' and value:
                    filters['grading__grading_datetime__date'] = value
                elif field_name == 'type' and value:
                    filters['grading__grading_type__exact'] = value
                else:
                    if value:
                        filters[field_name] = value
            
            # Apply all filters to the queryset in a single call
            queryset = queryset.filter(**filters)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = GradingInviteSearchForm(self.request.GET)
        # get initial values for the checkboxes
        selected_pks = self.request.GET.getlist('selected_items')
        pks = [int(pk) for pk in selected_pks]
        gradinginviteobjectlist = list(context['gradinginvite_list'].iterator())
        selected = []
        for giobj in gradinginviteobjectlist:
            selected.append(giobj.pk in pks)
        context['uselist'] = zip(selected, gradinginviteobjectlist)
        return context

class GradingInviteDelete(LoginRequiredMixin, DeleteView):
    model = GradingInvite
    success_url = reverse_lazy("dash-gradinginvites")

class GradingInviteCreate(CreatePopupMixin, LoginRequiredMixin, CreateView):
    model = GradingInvite
    form_class = GradingInviteForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get('_popup', False)
        c['popup'] = popup
        return c

    def get_initial(self):
        # Autofill the member field based on the 'member_id' parameter in the URL
        member_id = self.request.GET.get('member')
        grading = self.request.GET.get('grading')
        forbelt = self.request.GET.get('forbelt')

        i = {}
        if member_id:
            i['member'] = member_id

        if forbelt:
            i['forbelt'] = get_object_or_404(Belt, pk=forbelt)
        elif member_id:
            i['forbelt'] = get_object_or_404(Belt, pk=(int(Member.objects.get(id=member_id).belt.pk) + 1))

        if grading:
            i['grading'] = grading
            
        return i

class GradingInviteUpdate(UpdatePopupMixin, LoginRequiredMixin, UpdateView):
    model = GradingInvite
    form_class = GradingInviteForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get('_popup', False)
        c['popup'] = popup
        return c

@login_required
def gradinginvite_pdf_view(request, pk, **kwargs):
    gi = get_object_or_404(GradingInvite, pk=pk)
    data = {
        'gradinginvite': gi
    }
    return renderers.PDFResponse('dashboard/gradinginvite_pdf.html', f'GradingInvitation_{gi.member.first_name}{gi.member.last_name}_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf', data)

class GradingDetailView(LoginRequiredMixin, generic.DetailView):
    model = Grading

class GradingListView(LoginRequiredMixin, generic.ListView):
    model = Grading

    def get_queryset(self):
        queryset = Grading.objects.filter(style__pk=self.request.session.get('pk', 1)).all()
        return queryset

class GradingDelete(LoginRequiredMixin, DeleteView):
    model = Grading
    success_url = reverse_lazy("dash-gradings")

class GradingCreate(CreatePopupMixin, LoginRequiredMixin, CreateView):
    model = Grading
    form_class = GradingForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get('_popup', False)
        c['popup'] = popup
        return c

class GradingUpdate(UpdatePopupMixin, LoginRequiredMixin, UpdateView):
    model = Grading
    form_class = GradingForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get('_popup', False)
        c['popup'] = popup
        return c

@login_required
def gradingresult_pdf_view(request, pk, **kwargs):
    gr = get_object_or_404(GradingResult, pk=pk)
    data = {
        'gradingresult': gr
    }
    assessmentunits = gr.assessmentunit_set.all()
    if assessmentunits:
        maxpts = 0
        apts = 0
        for au in assessmentunits:
            maxpts += au.max_pts
            apts += au.achieved_pts
        if gr.is_letter:
            data['average_grade'] = LETTER_GRADES[round(apts/(len(assessmentunits)))]
        else:
            data['total_max_pts'] = maxpts
            data['total_achieved_pts'] = apts
            data['total_percent'] = round((data['total_achieved_pts']/data['total_max_pts'])*100)
    return renderers.PDFResponse('dashboard/gradingresult_pdf.html', f'GradingResult_{gr.member.first_name}{gr.member.last_name}_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf', data)

def gradingresult_batch_pdf_view(request, **kwargs):
    pks = request.GET.getlist('selected_items')
    if pks:
        merger = PdfWriter()
        buffer = BytesIO()
        for pk in pks:
            gr = get_object_or_404(GradingResult, pk=pk)
            data = {
                'gradingresult': gr
            }
            assessmentunits = gr.assessmentunit_set.all()
            if assessmentunits:
                maxpts = 0
                apts = 0
                for au in assessmentunits:
                    maxpts += au.max_pts
                    apts += au.achieved_pts
                if gr.is_letter:
                    data['average_grade'] = LETTER_GRADES[round(apts/(len(assessmentunits)))]
                else:
                    data['total_max_pts'] = maxpts
                    data['total_achieved_pts'] = apts
                    data['total_percent'] = round((data['total_achieved_pts']/data['total_max_pts'])*100)
            merger.append(PdfReader(renderers.render_to_pdf('dashboard/gradingresult_pdf.html', data)))
        merger.write(buffer)
        merger.close()

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="GradingResults_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf"'
        return response
    else:
        return HttpResponse(status=204)   

def gradinginvite_batch_pdf_view(request, **kwargs):
    pks = request.GET.getlist('selected_items')
    if pks:
        merger = PdfWriter()
        buffer = BytesIO()
        for pk in pks:
            gi = get_object_or_404(GradingInvite, pk=pk)
            data = {
                'gradinginvite': gi
            }
            merger.append(PdfReader(renderers.render_to_pdf('dashboard/gradinginvite_pdf.html', data)))
        merger.write(buffer)
        merger.close()

        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="GradingInvites_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf"'
        return response  
    else:
        return HttpResponse(status=204)

@permission_required("dashboard.add_gradingresult")
def gradinginvite_batch_create(request, **kwargs):
    GradingInviteFormSet = modelformset_factory(GradingInvite, form=GradingInviteBulkForm, extra=0)

    if request.method == "POST":
        formset = GradingInviteFormSet(request.POST, request.FILES, prefix="gradinginvites")
        gradingselectform = GradingSelectForm(prefix="miscselect")
        if formset.is_valid():
            # ADD ISSUED_BY AND CREATE/ADD PAYMENTS
            gi_pks = []
            for form in formset:
                if form.cleaned_data['select']:
                    gi = form.save(commit=False)
                    gi.issued_by = request.user
                    pt=12
                    p = Payment(member=form.cleaned_data['member'], paymenttype=get_object_or_404(PaymentType, pk=pt), amount_due=get_object_or_404(PaymentType, pk=pt).standard_amount)
                    p.save()
                    gi.payment = p
                    gi.save()
                    gi_pks.append(gi.pk)

            instances = formset.save(commit=False)
            qd = QueryDict(mutable=True)
            for pk in gi_pks:
                qd.update({'selected_items': pk})
            return HttpResponseRedirect(reverse('dash-batch-revise-grading-invite') + '?' + qd.urlencode())
    else:
        # GET request
        pks = request.GET.getlist('selected_items')
        GradingInviteFormSet = modelformset_factory(GradingInvite, form=GradingInviteBulkForm, extra=len(pks))
        formset = GradingInviteFormSet(initial=[{'member':pk, 'forbelt':get_object_or_404(Belt, pk=(get_object_or_404(Member, pk=pk).belt.pk + 1))} for pk in pks], queryset=GradingInvite.objects.none(), prefix="gradinginvites")
        gradingselectform = GradingSelectForm(prefix="miscselect")
    return render(request, "dashboard/gradinginvite_batch_create.html", {"formset": formset, 'miscform': gradingselectform})

@permission_required("dashboard.add_belt")
def manageBelts(request, **kwargs):
    BeltFormSet = modelformset_factory(Belt, form=BeltForm, formset=ConvenientBaseModelFormSet, can_delete=True, can_order=True)

    if request.method == "POST":
        formset = BeltFormSet(request.POST, request.FILES, prefix='belt-formset')
        if formset.is_valid():
            no_forms = len(formset)
            for i, form in enumerate(formset.ordered_forms):
                belt = form.save(commit=False)
                belt.degree = no_forms - i
                belt.save()
            instances = formset.save(commit=False)
            for obj in formset.deleted_objects:
                print(f'Deleting obj: {obj}')
                obj.delete()
        else:
            pass
    else:
        formset = BeltFormSet(prefix='belt-formset')
    return render(request, "dashboard/manage_belts.html", {"formset": formset})

@login_required
def batch_gradinginvite_revise(request, **kwargs):
    pks = request.GET.getlist('selected_items')
    gis = [get_object_or_404(GradingInvite, pk=pk) for pk in pks]

    url = reverse('dash-gradinginvites')+'?'
    for pk in pks:
        url += (f'selected_items={pk}&')
    url = url.strip('&')
    return render(request, "dashboard/gradinginvite_batch_revise.html", {'gradinginvites': gis, 'grading_invites_url': url})

@login_required
def gradingresult_batch_email_view(request, **kwargs):
    """
    View that sends emails with the GR PDF attached to the email the assessed member has on file
    GRs to be sent are specified by the selected_items query key
    """
    print('Email send request for gradingresults')
    try:
        pks = request.GET.getlist('selected_items')
    except:
        response_data = {'success': False, 'message': 'No items selected for email sending.'}
        return JsonResponse(response_data, status=204)
    if pks:
        messages = []
        for pk in pks:
            gr = get_object_or_404(GradingResult, pk=pk)
            data = {
                'gradingresult': gr
            }
            assessmentunits = gr.assessmentunit_set.all()
            if assessmentunits:
                maxpts = 0
                apts = 0
                for au in assessmentunits:
                    maxpts += au.max_pts
                    apts += au.achieved_pts
                if gr.is_letter:
                    data['average_grade'] = LETTER_GRADES[round(apts/(len(assessmentunits)))]
                else:
                    data['total_max_pts'] = maxpts
                    data['total_achieved_pts'] = apts
                    data['total_percent'] = round((data['total_achieved_pts']/data['total_max_pts'])*100)
            message = mail.EmailMessage(
                f'Grading Certificate for {gr.member}',
                'Please see attached your Grading Certificate.\n - TKD Manager.',
                'beaniemcc1@gmail.com',
                (f'{gr.member.email}',),
                attachments=[(f'GradingResult_{gr.member.first_name}{gr.member.last_name}_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf', renderers.render_to_pdf('dashboard/gradingresult_pdf.html', data).getvalue(), 'application/pdf')]
            )
            print(f'EmailMessage: {message}')
            messages.append(message)
        connection = mail.get_connection()  # Use default email connection
        connection.send_messages(messages)
        response_data = {'success': True, 'message': 'Emails sent successfully!'}
        return JsonResponse(response_data)
    else:
        response_data = {'success': False, 'message': 'No items selected for email sending.'}
        return JsonResponse(response_data, status=204)
    
@login_required
def gradinginvite_batch_email_view(request, **kwargs):
    """
    View that sends emails with the GI PDF attached to the email the assessed member has on file
    GIs to be sent are specified by the selected_items query key
    """
    print('Email send request for gradingresults')
    try:
        pks = request.GET.getlist('selected_items')
    except:
        response_data = {'success': False, 'message': 'No items selected for email sending.'}
        return JsonResponse(response_data, status=204)
    if pks:
        messages = []
        for pk in pks:
            gi = get_object_or_404(GradingInvite, pk=pk)
            data = {
                'gradinginvite': gi
            }
            # renderers.PDFResponse('dashboard/gradinginvite_pdf.html', f'GradingInvitation_{gi.member.first_name}{gi.member.last_name}_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf', data)
            message = mail.EmailMessage(
                f'Grading Invite for {gi.member}',
                'Please see attached your Grading Invite.\n - TKD Manager.',
                'beaniemcc1@gmail.com',
                (f'{gi.member.email}',),
                attachments=[(f'GradingInvitation_{gi.member.first_name}{gi.member.last_name}_{timezone.now().strftime("%d%m%y%H%M%S")}.pdf', renderers.render_to_pdf('dashboard/gradinginvite_pdf.html', data).getvalue(), 'application/pdf')]
            )
            print(f'EmailMessage: {message}')
            messages.append(message)
        connection = mail.get_connection()  # Use default email connection
        connection.send_messages(messages)
        response_data = {'success': True, 'message': 'Emails sent successfully!'}
        return JsonResponse(response_data)
    else:
        response_data = {'success': False, 'message': 'No items selected for email sending.'}
        return JsonResponse(response_data, status=204)
    
class RecurringPaymentDetailView(LoginRequiredMixin, generic.DetailView):
    model = RecurringPayment

class RecurringPaymentListView(LoginRequiredMixin, generic.ListView):
    model = RecurringPayment

    def get_queryset(self):
        manager = RecurringPayment.objects

        # Process form data to filter queryset
        form = RecurringPaymentSearchForm(self.request.GET)
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
        context['search_form'] = RecurringPaymentSearchForm(self.request.GET)
        return context 

class RecurringPaymentCreate(LoginRequiredMixin, CreateView):
    model = RecurringPayment
    form_class = RecurringPaymentForm

class RecurringPaymentUpdate(LoginRequiredMixin, UpdateView):
    model = RecurringPayment
    form_class = RecurringPaymentUpdateForm

class RecurringPaymentDelete(LoginRequiredMixin, DeleteView):
    model = RecurringPayment
    success_url = reverse_lazy("dash-rpayments")

class PaymentTypeCreate(CreatePopupMixin, LoginRequiredMixin, CreateView):
    model = PaymentType
    form_class = PaymentTypeForm

class PaymentTypeUpdate(UpdatePopupMixin, LoginRequiredMixin, UpdateView):
    model = PaymentType
    form_class = PaymentTypeForm

class PaymentTypeDelete(LoginRequiredMixin, DeleteView):
    model = PaymentType
    success_url = reverse_lazy("dash-payment-types")

class PaymentTypeDetailView(LoginRequiredMixin, generic.DetailView):
    model = PaymentType

class PaymentTypeListView(LoginRequiredMixin, generic.ListView):
    model = PaymentType

def selectStyle(request, pk):
    request.session['style'] = pk
    return HttpResponse()