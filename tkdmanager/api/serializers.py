from django.contrib.auth.models import User
from rest_framework import serializers, fields
from dashboard.models import GradingResult, AssessmentUnit, GradingInvite, Payment, PaymentType, Grading


class UserSerializer(serializers.HyperlinkedModelSerializer):
    extra_kwargs = {'url': {'view_name': 'api:user-detail'}}

    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class AssessmentUnitSerializer(serializers.HyperlinkedModelSerializer):
    extra_kwargs = {'url': {'view_name': 'api:assessmentunit-detail'}}

    class Meta:
        model = AssessmentUnit
        fields = ['url','unit','achieved_pts','max_pts','grading_result']


class GradingResultSerializer(serializers.HyperlinkedModelSerializer):
    assessmentunits = AssessmentUnitSerializer(many=True, read_only=True)
    extra_kwargs = {'url': {'view_name': 'api:gradingresult-detail'}}

    class Meta:
        model = GradingResult
        fields = ['url','member','grading','forbelt','assessor','comments','award', 'assessmentunits','is_letter','gradinginvite']

class GradingInviteSerializer(serializers.HyperlinkedModelSerializer):
    extra_kwargs = {'url': {'view_name': 'api:gradinginvite-detail'}}

    class Meta:
        model = GradingInvite
        fields = ['url','member', 'forbelt', 'issued_by', 'payment', 'grading']

class PaymentSerializer(serializers.HyperlinkedModelSerializer):
    extra_kwargs = {'url': {'view_name': 'api:payment-detail'}}

    class Meta:
        model = Payment
        fields = ['url','member','paymenttype','date_created','date_due','date_paid_in_full','amount_due','amount_paid']
    
class GradingSerializer(serializers.HyperlinkedModelSerializer):
    extra_kwargs = {'url': {'view_name': 'api:grading-detail'}}

    class Meta:
        model = Grading
        fields = ['url','grading_type','grading_datetime']

class PaymentTypeSerialzer(serializers.HyperlinkedModelSerializer):
    extra_kwargs = {'url': {'view_name': 'api:paymenttype-detail'}}

    class Meta:
        model = PaymentType
        fields = ['url','name','standard_amount']
    
