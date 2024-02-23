from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"user", views.UserViewSet)
router.register(r"member", views.MemberViewSet)
router.register(r"gradingresult", views.GradingResultViewSet)
router.register(r"gradinginvite", views.GradingInviteViewSet)
router.register(r"grading", views.GradingViewSet)
router.register(r"payment", views.PaymentViewSet)
router.register(r"paymenttype", views.PaymentTypeViewSet)
router.register(r"award", views.AwardViewSet)
router.register(r"class", views.ClassViewSet)
router.register(r"belt", views.BeltViewSet)
router.register(r"recurringpayment", views.RecurringPaymentViewSet)
router.register(r"memberproperty", views.MemberPropertyViewSet)
router.register(r"memberpropertytype", views.MemberPropertyTypeViewSet)
router.register(r"assessmentunittype", views.AssessmentUnitTypeViewSet)
router.register(r"classtype", views.ClassTypeViewSet)
router.register(r"gradingtype", views.GradingTypeViewSet)
router.register(r"style", views.StyleViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
