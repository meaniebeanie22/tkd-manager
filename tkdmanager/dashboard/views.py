from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from .models import Member, Award, AssessmentUnit, GradingResult, Class, Payment, PaymentType, GradingInvite, Grading, GRADINGS, LETTER_GRADES, determine_belt_type
from django.views import generic, View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy, reverse
from datetime import date, datetime, timedelta
from django.forms import inlineformset_factory, modelformset_factory, Form, ModelChoiceField, ModelForm, BooleanField
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, QueryDict
from .forms import GradingResultCreateForm, GradingResultUpdateForm, ClassForm, GradingResultSearchForm, MemberForm, PaymentForm, AssessmentUnitLetterForm, GradingInviteForm, GradingForm, GradingInviteSearchForm, ClassSearchForm, PaymentSearchForm
from django.db.models import Q
from dashboard import renderers
from django.forms.models import model_to_dict
from rest_framework.authtoken.models import Token
from io import BytesIO
from pypdf import PdfWriter, PdfReader
from django_addanother.views import CreatePopupMixin, UpdatePopupMixin
from django.core import mail

def time_difference_in_seconds(time1, time2):
    # Convert time objects to timedelta
    delta = datetime.combine(datetime.today(), time2) - datetime.combine(datetime.today(), time1)
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

    context = {
        'num_members': num_members,
        'num_active_members': num_active_members,
        'belt_labels': ["None","White","Orange","Yellow","Blue","Red","CDB","Black"],
        'belt_count': [Member.objects.filter(belt__exact=None).count(),Member.objects.filter(belt__in=tuple(range(8))).count(),Member.objects.filter(belt__in=tuple(range(8,16))).count(),Member.objects.filter(belt__in=tuple(range(16,24))).count(),Member.objects.filter(belt__in=tuple(range(24,32))).count(),Member.objects.filter(belt__in=tuple(range(32,39))).count(),Member.objects.filter(belt__in=tuple(range(39,47))).count(),Member.objects.filter(belt__in=tuple(range(47,56))).count()]
    }

    return render(request, 'home.html', context=context)

@login_required
def token_display(request):
    token = Token.objects.get_or_create(user=request.user)
    context = {
        'token': token
    }

    return render(request, 'token.html', context=context)

class MemberListView(LoginRequiredMixin, generic.ListView):
    model = Member
    ordering = ['-belt','last_name']

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Member.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(idnumber__icontains=query) | Q(email__icontains=query) | Q(phone__iexact=query))
        else:
            return Member.objects.all()

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
        today = datetime.now().date()
        six_months_later = today + timedelta(days=6 * 30)
        six_months_before = today - timedelta(days=6 * 30)
        recent_payments = self.get_object().payment_set.filter(Q(date_due__date__gte=six_months_before) & Q(date_due__date__lte=six_months_later)).all()
        payments = self.get_object().payment_set.all()
        overdue_payments = [p for p in payments if p.get_payment_status() == "Overdue"]
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
        queryset = GradingResult.objects.all()

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
            i['forbelt'] = int(Member.objects.get(id=member_id).belt) + 1
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
    AssessmentUnitInlineFormSet = inlineformset_factory(GradingResult, AssessmentUnit, fields=['unit','achieved_pts','max_pts'], extra=10-gradingresult.assessmentunit_set.all().count())
    
    if request.method == "POST":
        formset = AssessmentUnitInlineFormSet(request.POST, request.FILES, instance=gradingresult)
        if formset.is_valid():
            formset.save()
            # Do something. Should generally end with a redirect. For example:
            return HttpResponseRedirect(gradingresult.get_absolute_url())
    else:
        formset = AssessmentUnitInlineFormSet(instance=gradingresult)
    return render(request, 'dashboard/gradingresult_form2.html', {'formset': formset})

@permission_required("dashboard.change_gradingresult")
def manageGradingResultLetter(request, **kwargs):
    gradingresult = GradingResult.objects.get(pk=kwargs['pk'])
    AssessmentUnitInlineFormSet = inlineformset_factory(GradingResult, AssessmentUnit, form=AssessmentUnitLetterForm, extra=10-gradingresult.assessmentunit_set.all().count())
    
    if request.method == "POST":
        formset = AssessmentUnitInlineFormSet(request.POST, request.FILES, instance=gradingresult)
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
        formset = AssessmentUnitInlineFormSet(instance=gradingresult)
    return render(request, 'dashboard/gradingresult_form2.html', {'formset': formset})    

class ClassListView(LoginRequiredMixin, generic.ListView):
    model = Class

    def get_queryset(self):
        queryset = Class.objects.all()

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
        url = reverse('dash-batch-create-grading-invite')+'?'
        for student in cl.students.all():
            url += (f'selected_items={student.pk}&')
        url = url.strip('&')
        context['batch_create_grading_invites_url'] = url
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
        queryset = Payment.objects.all()

        # Process form data to filter queryset
        form = PaymentSearchForm(self.request.GET)
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
            'forbelt': gradinginvite.forbelt,
            'gradingpk': gradinginvite.grading.pk,
        }
        return JsonResponse(response)
    
class MemberGetGradingInvites(LoginRequiredMixin, View):
    def get(self, request, pk):
        selected_member = get_object_or_404(Member, pk=pk)

        today = datetime.now().date()
        six_months_before = today - timedelta(days=6 * 30)

        grading_invites = selected_member.gradinginvite_set.filter(grading__grading_datetime__date__gte=six_months_before).all()

        data = [{'value': invite.id, 'label': str(invite)} for invite in grading_invites]
        return JsonResponse(data, safe=False)

class MemberGetPayments(LoginRequiredMixin, View):
    def get(self, request, pk):
        selected_member = get_object_or_404(Member, pk=pk)

        today = datetime.now().date()
        six_months_before = today - timedelta(days=6 * 30)

        payments = selected_member.payment_set.filter(date_created__gte=six_months_before).all().order_by("-date_created")

        data = [{'value': payment.id, 'label': str(payment)} for payment in payments]
        return JsonResponse(data, safe=False)
    
class MemberGetDetails(LoginRequiredMixin, View):
    def get(self, request, pk):
        selected_member = get_object_or_404(Member, pk=pk)
        data = model_to_dict(selected_member)
        return JsonResponse(data, safe=False)

class GradingInviteDetailView(LoginRequiredMixin, generic.DetailView):
    model = GradingInvite

class GradingInviteListView(LoginRequiredMixin, generic.ListView):
    model = GradingInvite

    def get_queryset(self):
        queryset = GradingInvite.objects.all()

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
        return context

class GradingInviteDeleteView(LoginRequiredMixin, DeleteView):
    model = GradingInvite
    success_url = reverse_lazy("dash-gradinginvites")

class GradingInviteCreateView(CreatePopupMixin, LoginRequiredMixin, CreateView):
    model = GradingInvite
    form_class = GradingInviteForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get('_popup', False)
        c['popup'] = popup
        return c

    def get_initial(self):
        # Autofill the member field based on the 'member_id' parameter in the URL
        member_id = self.request.GET.get('member_id')
        i = {}
        if member_id:
            i['member'] = member_id
            i['forbelt'] = int(Member.objects.get(id=member_id).belt) + 1
        return i

class GradingInviteUpdateView(UpdatePopupMixin, LoginRequiredMixin, UpdateView):
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
    return renderers.PDFResponse('dashboard/gradinginvite_pdf.html', f'GradingInvitation_{gi.member.first_name}{gi.member.last_name}_{datetime.now().strftime("%d%m%y%H%M%S")}.pdf', data)

class GradingDetailView(LoginRequiredMixin, generic.DetailView):
    model = Grading

class GradingListView(LoginRequiredMixin, generic.ListView):
    model = Grading

class GradingDeleteView(LoginRequiredMixin, DeleteView):
    model = Grading
    success_url = reverse_lazy("dash-gradings")

class GradingCreateView(CreatePopupMixin, LoginRequiredMixin, CreateView):
    model = Grading
    form_class = GradingForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        c = super().get_context_data(**kwargs)
        popup = self.request.GET.get('_popup', False)
        c['popup'] = popup
        return c

class GradingUpdateView(UpdatePopupMixin, LoginRequiredMixin, UpdateView):
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
    return renderers.PDFResponse('dashboard/gradingresult_pdf.html', f'GradingResult_{gr.member.first_name}{gr.member.last_name}_{datetime.now().strftime("%d%m%y%H%M%S")}.pdf', data)

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
        response['Content-Disposition'] = f'attachment; filename="GradingResults_{datetime.now().strftime("%d%m%y%H%M%S")}.pdf"'
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
        response['Content-Disposition'] = f'attachment; filename="GradingInvites_{datetime.now().strftime("%d%m%y%H%M%S")}.pdf"'
        return response  
    else:
        return HttpResponse(status=204)

class GradingSelectForm(Form):
    grading = ModelChoiceField(queryset=Grading.objects.all(), required=False)

class GradingInviteBulkForm(ModelForm):
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
                    belt = determine_belt_type(gi.forbelt)
                    # hardcoded values for blackbelt and coloured belt payment type pks bleuhh
                    if belt == 'Black':
                        pt=13
                    else:
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
        formset = GradingInviteFormSet(initial=[{'member':pk, 'forbelt':(get_object_or_404(Member, pk=pk).belt + 1)} for pk in pks], queryset=GradingInvite.objects.none(), prefix="gradinginvites")
        gradingselectform = GradingSelectForm(prefix="miscselect")
    return render(request, "dashboard/gradinginvite_batch_create.html", {"formset": formset, 'miscform': gradingselectform})

@login_required
def batch_gradinginvite_revise(request, **kwargs):
    pks = request.GET.getlist('selected_items')
    gis = [get_object_or_404(GradingInvite, pk=pk) for pk in pks]

    url = reverse('dash-batch-generate-gi-pdf')+'?'
    for pk in pks:
        url += (f'selected_items={pk}&')
    url = url.strip('&')
    return render(request, "dashboard/gradinginvite_batch_revise.html", {'gradinginvites': gis, 'batch_download_grading_invites_url': url})

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
                attachments=[(f'GradingResult_{gr.member.first_name}{gr.member.last_name}_{datetime.now().strftime("%d%m%y%H%M%S")}.pdf', renderers.render_to_pdf('dashboard/gradingresult_pdf.html', data).getvalue(), 'application/pdf')]
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
            # renderers.PDFResponse('dashboard/gradinginvite_pdf.html', f'GradingInvitation_{gi.member.first_name}{gi.member.last_name}_{datetime.now().strftime("%d%m%y%H%M%S")}.pdf', data)
            message = mail.EmailMessage(
                f'Grading Invite for {gi.member}',
                'Please see attached your Grading Invite.\n - TKD Manager.',
                'beaniemcc1@gmail.com',
                (f'{gi.member.email}',),
                attachments=[(f'GradingInvitation_{gi.member.first_name}{gi.member.last_name}_{datetime.now().strftime("%d%m%y%H%M%S")}.pdf', renderers.render_to_pdf('dashboard/gradinginvite_pdf.html', data).getvalue(), 'application/pdf')]
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