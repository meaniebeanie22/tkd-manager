from dashboard.models import (AssessmentUnit, Award, Class, Grading,
                              GradingInvite, GradingResult, Member, Payment,
                              PaymentType, MemberProperty, MemberPropertyType,
                              RecurringPayment, Belt)
from django.contrib.auth.models import User
from rest_framework import viewsets

from .permissions import APIAllowed
from .serializers import *


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

class BeltViewSet(viewsets.ModelViewSet):
    """
    API endpoint for belts
    """
    queryset = Belt.objects.all()
    serializer_class = BeltSerializer
    permission_classes = [APIAllowed]

class MemberPropertyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for member properties
    """
    queryset = MemberProperty.objects.all()
    serializer_class = MemberPropertySerializer
    permission_classes = [APIAllowed]

class MemberPropertyTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for member property types
    """
    queryset = MemberPropertyType.objects.all()
    serializer_class = MemberPropertyTypeSerializer
    permission_classes = [APIAllowed]

class RecurringPaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for recurring payments
    """
    queryset = RecurringPayment.objects.all()
    serializer_class = RecurringPaymentSerializer
    permission_classes = [APIAllowed]

class GradingTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for grading types
    """
    queryset = GradingType.objects.all()
    serializer_class = GradingTypeSerializer
    permission_classes = [APIAllowed]

class ClassTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for class types
    """
    queryset = ClassType.objects.all()
    serializer_class = ClassTypeSerializer
    permission_classes = [APIAllowed]

class AssessmentUnitTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint for assessmentunittypes
    """
    queryset = AssessmentUnitType.objects.all()
    serializer_class = AssessmentUnitTypeSerializer
    permission_classes = [APIAllowed]

class StyleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for styles
    """
    queryset = Style.objects.all()
    serializer_class = StyleSerializer
    permission_classes = [APIAllowed]