from django import forms
from dashboard.models import Member, GradingResult, AssessmentUnit, Award
import datetime
from dashboard.models import GRADINGS, BELT_CHOICES

class AddMemberModelForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name','last_name','idnumber','address_line_1','address_line_2','address_line_3','date_of_birth','belt','email','phone','team_leader_instructor','active']

class GradingResultForm(forms.Form):
    member = forms.ModelChoiceField(queryset=Member.objects.all(), empty_label=None)
    date = forms.DateField(initial=datetime.date.today())
    type = forms.ChoiceField(choices=GRADINGS)
    assessor = forms.ModelMultipleChoiceField(queryset=Member.objects.all())
    forbelt = forms.ChoiceField(choices=BELT_CHOICES)
    comments = forms.CharField(max_length=200)
    award = forms.ModelChoiceField(queryset=Award.objects.all())

"""
class Meta:
    model = GradingResult
    fields = ['member','date','type','assessor','forbelt','comments','award']
"""
        
class AddAssessmentUnitModelForm(forms.ModelForm):
    class Meta:
        model = AssessmentUnit
        fields = ['unit', 'achieved_pts', 'max_pts', 'grading_result']