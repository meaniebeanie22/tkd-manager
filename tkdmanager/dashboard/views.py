from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from .models import Member, Award, AssessmentUnit, GradingResult, Class, Payment, PaymentType, GRADINGS, LETTER_GRADES
from django.views import generic, View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from datetime import date, datetime, timedelta
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import GradingResultCreateForm, GradingResultUpdateForm, ClassForm, GradingResultSearchForm, MemberForm, PaymentForm, AssessmentUnitLetterForm
from django.db.models import Q
from django.utils import timezone

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
        'belt_count': [Member.objects.filter(belt__exact='').count(),Member.objects.filter(belt__in=('0','1','2','3','4','5','6','7')).count(),Member.objects.filter(belt__in=('8','9','10','11','12','13','14','15')).count(),Member.objects.filter(belt__in=('16','17','18','19','20','21','22','23')).count(),Member.objects.filter(belt__in=('24','25','26','27','28','29','30','31')).count(),Member.objects.filter(belt__in=('32','33','34','35','36','37','38')).count(),Member.objects.filter(belt__in=('39','40','41','42','43','44','45','46')).count(),Member.objects.filter(belt__in=('47','48','49','50','51','52','53','54','55')).count()]
    }

    return render(request, 'home.html', context=context)

class MemberListView(LoginRequiredMixin, generic.ListView):
    model = Member
    paginate_by = 25
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
        recent_payments = self.get_object().payment_set.filter(Q(date_due__date__gte=today) & Q(date_due__date__lte=six_months_later)).all()
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


    """
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(GradingResultDetailView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        maxpts = 0
        apts = 0
        if self.get_object().assessmentunit_set.all():
            for au in self.get_object().assessmentunit_set.all():
                maxpts += au.max_pts
                apts += au.achieved_pts

            context['total_max_pts'] = maxpts
            context['total_achieved_pts'] = apts
            context['total_percent'] = round((context['total_achieved_pts']/context['total_max_pts'])*100)

        
        return context
    """
    
class GradingResultListView(LoginRequiredMixin, generic.ListView):
    model = GradingResult
    paginate_by = 25

    def get_queryset(self):
        queryset = GradingResult.objects.all()

        # Process form data to filter queryset
        form = GradingResultSearchForm(self.request.GET)
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
    success_url = reverse_lazy("members")

class GradingResultCreate(LoginRequiredMixin, CreateView):
    form_class = GradingResultCreateForm
    model = GradingResult
    template_name = 'dashboard/gradingresult_form.html'

    def form_valid(self, form):
        response = super(GradingResultCreate, self).form_valid(form)
        # do something with self.object
        target = self.object.member
        target.belt = target.member2gradings.order_by('-date').first().forbelt
        target.save()
        return response

    def get_success_url(self):
        if self.object.is_letter:
            return reverse('update-grading-result3', kwargs={'pk':self.object.pk})
        else:
            return reverse('update-grading-result2', kwargs={'pk':self.object.pk})
    
    def get_initial(self):
        # Autofill the member field based on the 'member_id' parameter in the URL
        member_id = self.request.GET.get('member_id')
        i = {}
        if member_id:
            i['member'] = member_id
            i['forbelt'] = int(Member.objects.get(id=member_id).belt) + 1


        i['date'] = date.today()
        return i

class GradingResultUpdate(LoginRequiredMixin, UpdateView):
    form_class = GradingResultUpdateForm
    template_name = 'dashboard/gradingresult_form.html'
    model = GradingResult

    def form_valid(self, form):
        response = super(GradingResultUpdate, self).form_valid(form)
        # do something with self.object
        target = self.object.member
        target.belt = target.member2gradings.order_by('-date').first().forbelt
        target.save()
        return response
    
    def get_success_url(self):
        if self.object.is_letter:
            return reverse('update-grading-result3', kwargs={'pk':self.object.pk})
        else:
            return reverse('update-grading-result2', kwargs={'pk':self.object.pk})

class GradingResultDelete(LoginRequiredMixin, DeleteView):
    model = GradingResult
    success_url = reverse_lazy("gradingresults")

class AwardListView(LoginRequiredMixin, generic.ListView):
    model = Award

class AwardCreate(LoginRequiredMixin, CreateView):
    model = Award
    fields = ['name']

class AwardUpdate(LoginRequiredMixin, UpdateView):
    model = Award
    fields = ['name']

class AwardDelete(LoginRequiredMixin, DeleteView):
    model = Award
    success_url = reverse_lazy("awards")

class AwardDetailView(LoginRequiredMixin, generic.DetailView):
    model = Award

@login_required 
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

@login_required
def manageGradingResultLetter(request, **kwargs):
    gradingresult = GradingResult.objects.get(pk=kwargs['pk'])
    AssessmentUnitInlineFormSet = inlineformset_factory(GradingResult, AssessmentUnit, form=AssessmentUnitLetterForm, extra=10-gradingresult.assessmentunit_set.all().count())
    
    if request.method == "POST":
        formset = AssessmentUnitInlineFormSet(request.POST, request.FILES, instance=gradingresult)
        if formset.is_valid():
            for form in formset:
                unit = form.cleaned_data.get('unit')
                print(f'Unit: {unit}')
                if form.cleaned_data.get('unit'):
                    print("Saved!")
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
    paginate_by = 25

    def get_queryset(self):
        type = self.request.GET.get('type')
        date_str = self.request.GET.get('date')
        if not (type or date_str):
            return Class.objects.all()
        else:
            queryset = Class.objects.all()
            if type:
                type = type.lower()
                backwards = {x[1]:x[0] for x in GRADINGS}
                type = backwards.get(type, type)
                queryset = queryset.filter(Q(type__icontains=type))
            if date_str:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(Q(date=date))
            return queryset           
        
class ClassDetailView(LoginRequiredMixin, generic.DetailView):
    model = Class

class ClassCreate(LoginRequiredMixin, CreateView):
    model = Class
    form_class = ClassForm

class ClassUpdate(LoginRequiredMixin, UpdateView):
    model = Class
    form_class = ClassForm

class ClassDelete(LoginRequiredMixin, DeleteView):
    model = Class
    success_url = reverse_lazy("classes")

class PaymentListView(LoginRequiredMixin, generic.ListView):
    model = Payment
    paginate_by = 25

class PaymentDetailView(LoginRequiredMixin, generic.DetailView):
    model = Payment

class PaymentCreate(LoginRequiredMixin, CreateView):
    model = Payment
    form_class = PaymentForm

class PaymentUpdate(LoginRequiredMixin, UpdateView):
    model = Payment
    form_class = PaymentForm

class PaymentDelete(LoginRequiredMixin, DeleteView):
    model = Payment
    success_url = reverse_lazy("payments")

class GetStandardAmountView(LoginRequiredMixin, View):
    def get(self, request, pk):
        payment_type = get_object_or_404(PaymentType, pk=pk)
        standard_amount = payment_type.standard_amount
        return JsonResponse({'standard_amount': standard_amount})