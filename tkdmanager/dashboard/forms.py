from django import forms
from dashboard.models import Member, GradingResult, AssessmentUnit, Award
import datetime
from dashboard.models import GRADINGS, BELT_CHOICES

class AddMemberModelForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['first_name','last_name','idnumber','address_line_1','address_line_2','address_line_3','date_of_birth','belt','email','phone','team_leader_instructor','active']

