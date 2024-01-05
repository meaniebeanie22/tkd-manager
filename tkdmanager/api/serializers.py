from django.contrib.auth.models import User
from rest_framework import serializers, fields
from dashboard.models import GradingResult, AssessmentUnit, GradingInvite, Payment, PaymentType, Grading


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']
        extra_kwargs = {'url': {'view_name': 'api:user-detail'}}

class AssessmentUnitSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssessmentUnit
        fields = ['url','unit','achieved_pts','max_pts','grading_result']
        extra_kwargs = {'url': {'view_name': 'api:assessmentunit-detail'}}


class GradingResultSerializer(serializers.HyperlinkedModelSerializer):
    assessmentunits = AssessmentUnitSerializer(many=True, read_only=True)
    class Meta:
        model = GradingResult
        fields = ['url','member','grading','forbelt','assessor','comments','award', 'assessmentunits','is_letter','gradinginvite']
        extra_kwargs = {'url': {'view_name': 'api:gradingresult-detail'}}

class GradingInviteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GradingInvite
        fields = ['url','member', 'forbelt', 'issued_by', 'payment', 'grading']
        extra_kwargs = {'url': {'view_name': 'api:gradinginvite-detail'}}

class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Payment
        fields = ['url','member','paymenttype','date_created','date_due','date_paid_in_full','amount_due','amount_paid']
        extra_kwargs = {'url': {'view_name': 'api:payment-detail'}}
    
class GradingSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Grading
        fields = ['url','grading_type','grading_datetime']
        extra_kwargs = {'url': {'view_name': 'api:grading-detail'}}

class PaymentTypeSerialzer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PaymentType
        fields = ['url','name','standard_amount']
        extra_kwargs = {'url': {'view_name': 'api:paymenttype-detail'}}
    
