from django.contrib.auth.models import User
from dashboard.models import GradingResult, AssessmentUnit
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UserSerializer, GradingResultSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class GradingResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows grading results to be viewed or edited.
    """
    queryset = GradingResult.objects.all()
    serializer_class = GradingResultSerializer
    permission_classes = [permissions.IsAuthenticated]
