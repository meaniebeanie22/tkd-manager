from typing import Any
from django.shortcuts import render
from .models import Member, Award, AssessmentUnit, GradingResult, Class
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from datetime import date
from django.forms import inlineformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from .forms import GradingResultForm
from django.db.models import Q


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
    paginate_by = 15
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
        print(f'Object = {self.get_object}')
        classes_taught = self.get_object().instructors2classes.all()
        print(f'Classes Taught = {classes_taught}')
        seconds = 0
        for cl in classes_taught:
            length = cl.end - cl.start
            seconds += length.total_seconds()
        hours = round(seconds/3600, 2)
        context['hours_taught'] = hours
        return context

class GradingResultDetailView(LoginRequiredMixin, generic.DetailView):
    model = GradingResult

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
    
class GradingResultListView(LoginRequiredMixin, generic.ListView):
    model = GradingResult
    paginate_by = 15
    
class MemberCreate(LoginRequiredMixin, CreateView):
    model = Member
    fields = ['first_name','last_name','idnumber','address_line_1','address_line_2','address_line_3','date_of_birth','belt','email','phone','team_leader_instructor','active']

class MemberUpdate(LoginRequiredMixin, UpdateView):
    model = Member
    fields = ['first_name','last_name','idnumber','address_line_1','address_line_2','address_line_3','date_of_birth','belt','email','phone','team_leader_instructor','active']

class MemberDelete(LoginRequiredMixin, DeleteView):
    model = Member
    success_url = reverse_lazy("members")

class GradingResultCreate(LoginRequiredMixin, CreateView):
    form_class = GradingResultForm
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
    form_class = GradingResultForm
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

class ClassListView(LoginRequiredMixin, generic.ListView):
    model = Class
    paginate_by = 15

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Class.objects.filter(Q(start__iexact=query) | Q(end__iexact=query) | Q(type__icontains=query))
        else:
            return Class.objects.all()
        
class ClassDetailView(LoginRequiredMixin, generic.DetailView):
    model = Class

class ClassCreate(LoginRequiredMixin, CreateView):
    model = Class
    fields = ['type','start','end','instructors','students']

class ClassUpdate(LoginRequiredMixin, UpdateView):
    model = Class
    fields = ['type','start','end','instructors','students']

class ClassDelete(LoginRequiredMixin, DeleteView):
    model = Class
    success_url = reverse_lazy("classes")

