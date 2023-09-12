from django.shortcuts import render
from .models import Member, Award, AssessmentUnit, GradingResult
from django.views import generic

# Create your views here.

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

class MemberListView(generic.ListView):
    model = Member
    paginate_by = 25

class MemberDetailView(generic.DetailView):
    model = Member

class GradingResultDetailView(generic.DetailView):
    model = GradingResult

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(GradingResultDetailView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        maxpts = 0
        apts = 0
        for au in self.get_object().assessmentunit_set.all():
            maxpts += au.max_pts
            apts += au.achieved_pts

        context['total_max_pts'] = maxpts
        context['total_achieved_pts'] = apts
        context['total_percent'] = round((context['total_achieved_pts']/context['total_max_pts'])*100)
        return context

