from django.contrib.auth.models import User
from rest_framework import serializers, fields
from dashboard.models import GradingResult, AssessmentUnit, GradingInvite, Payment, PaymentType, Grading, Member, Award


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email']

class AssessmentUnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssessmentUnit
        fields = ['url','unit','achieved_pts','max_pts','grading_result']

class MemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Member 
        fields = ['first_name','last_name','idnumber','address_line_1','address_line_2','address_line_3','date_of_birth','belt','email','phone','team_leader_instructor','active']

class GradingResultSerializer(serializers.HyperlinkedModelSerializer):
    assessmentunits = AssessmentUnitSerializer(many=True, read_only=True)
    class Meta:
        model = GradingResult
        fields = ['url','member','grading','forbelt','assessor','comments','award', 'assessmentunits','is_letter','gradinginvite']

class GradingInviteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GradingInvite
        fields = ['url','member', 'forbelt', 'issued_by', 'payment', 'grading']

class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = ['url','member','paymenttype','date_created','date_due','date_paid_in_full','amount_due','amount_paid']
    
class GradingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Grading
        fields = ['url','grading_type','grading_datetime']

class PaymentTypeSerialzer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PaymentType
        fields = ['url','name','standard_amount']

class AwardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Award
        fields = ['name']
    
