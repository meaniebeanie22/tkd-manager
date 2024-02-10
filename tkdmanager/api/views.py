from dashboard.models import (AssessmentUnit, Award, Class, Grading,
                              GradingInvite, GradingResult, Member, Payment,
                              PaymentType)
from django.contrib.auth.models import User
from rest_framework import viewsets

from .permissions import APIAllowed
from .serializers import (AssessmentUnitSerializer, AwardSerializer,
                          ClassSerializer, GradingInviteSerializer,
                          GradingResultSerializer, GradingSerializer,
                          MemberSerializer, PaymentSerializer,
                          PaymentTypeSerialzer, UserSerializer)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [APIAllowed]

class GradingResultViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows grading results and their assessment units to be viewed, and grading results to be edited.
    """
    queryset = GradingResult.objects.all()
    serializer_class = GradingResultSerializer
    permission_classes = [APIAllowed]

class AssessmentUnitViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assessment units to be viewed or edited.
    """
    queryset = AssessmentUnit.objects.all()
    serializer_class = AssessmentUnitSerializer
    permission_classes = [APIAllowed]

class GradingInviteViewSet(viewsets.ModelViewSet):
    """
    API endpoint for gradinginvites
    """
    queryset = GradingInvite.objects.all()
    serializer_class = GradingInviteSerializer
    permission_classes = [APIAllowed]

class GradingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for gradings
    """
    queryset = Grading.objects.all()
    serializer_class = GradingSerializer
    permission_classes = [APIAllowed]

class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payments
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [APIAllowed]

class PaymentTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for payment types
    """
    queryset = PaymentType.objects.all()
    serializer_class = PaymentTypeSerialzer
    permission_classes = [APIAllowed]

class MemberViewSet(viewsets.ModelViewSet):
    """
    API endpoint for members
    """
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    permission_classes = [APIAllowed]

class AwardViewSet(viewsets.ModelViewSet):
    """
    API endpoint for awards
    """
    queryset = Award.objects.all()
    serializer_class = AwardSerializer
    permission_classes = [APIAllowed]

class ClassViewSet(viewsets.ModelViewSet):
    """
    API endpoint for classes
    """
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    permission_classes = [APIAllowed]
