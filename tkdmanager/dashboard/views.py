from django.shortcuts import render
from .models import Member, Award, AssessmentUnit, GradingResult
from django.views import generic
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
import datetime
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect


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
    print(context['belt_count'])

    return render(request, 'home.html', context=context)

class MemberListView(LoginRequiredMixin, generic.ListView):
    model = Member
    paginate_by = 15

class MemberDetailView(LoginRequiredMixin, generic.DetailView):
    model = Member

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
    
class MemberCreate(LoginRequiredMixin, CreateView):
    model = Member
    fields = ['first_name','last_name','idnumber','address_line_1','address_line_2','address_line_3','date_of_birth','belt','email','phone','team_leader_instructor','active']

class MemberUpdate(LoginRequiredMixin, UpdateView):
    model = Member
    fields = ['first_name','last_name','idnumber','address_line_1','address_line_2','address_line_3','date_of_birth','belt','email','phone','team_leader_instructor','active']

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
    return render(request, 'gradingresult_form.html', {'formset': formset})

