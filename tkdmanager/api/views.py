from django.contrib.auth.models import User
from dashboard.models import GradingResult, AssessmentUnit
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UserSerializer, GradingResultSerializer, AssessmentUnitSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class GradingResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows grading results and their assessment units to be viewed, and grading results to be edited.
    """
    queryset = GradingResult.objects.all()
    serializer_class = GradingResultSerializer
    permission_classes = [permissions.IsAuthenticated]

class AssessmentUnitViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assessment units to be viewed or edited.
    """
    queryset = AssessmentUnit.objects.all()
    serializer_class = AssessmentUnitSerializer
    permission_classes = [permissions.IsAuthenticated]