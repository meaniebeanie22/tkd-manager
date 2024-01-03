from django.contrib.auth.models import User
from rest_framework import serializers, fields
from dashboard.models import GradingResult, AssessmentUnit, GradingInvite, Payment, PaymentType, Grading


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class AssessmentUnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssessmentUnit
        fields = ['unit','achieved_pts','max_pts','grading_result']


class GradingResultSerializer(serializers.HyperlinkedModelSerializer):
    assessmentunits = AssessmentUnitSerializer(many=True, read_only=True)

    class Meta:
        model = GradingResult
        fields = ['member','grading','forbelt','assessor','comments','award', 'assessmentunits','is_letter','gradinginvite']

class GradingInviteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GradingInvite
        fields = ['member', 'forbelt', 'issued_by', 'payment', 'grading']

class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = ['member','paymenttype','date_created','date_due','date_paid_in_full','amount_due','amount_paid']
    
class GradingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Grading
        fields = ['grading_type','grading_datetime']

class PaymentTypeSerialzer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PaymentType
        fields = ['name','standard_amount']
    
