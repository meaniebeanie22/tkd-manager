from django.contrib.auth.models import User
from rest_framework import serializers, fields
from dashboard.models import GradingResult, AssessmentUnit, GradingInvite


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
        fields = ['member','grading','forbelt','assessor','comments','award', 'assessmentunits','is_letter']
    
