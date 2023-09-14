from django.forms import ModelForm
from dashboard.models import Member, GradingResult

class AddMemberModelForm(ModelForm):
    class Meta:
        model = Member
        fields = ['first_name','last_name','idnumber','address_line_1','address_line_2','address_line_3','date_of_birth','belt','awards','email','phone','team_leader_instructor','active']

class AddGradingResultModelForm(ModelForm):
    class Meta:
        model = GradingResult
        fields = ['member','date','type','assessor','forbelt','comments']