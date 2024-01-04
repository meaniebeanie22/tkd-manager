from django.urls import include, path
from rest_framework import routers
from . import views

app_name = "api"

router = routers.DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'gradingresult', views.GradingResultViewSet)
router.register(r'gradinginvite', views.GradingInviteViewSet)
router.register(r'grading', views.GradingViewSet)
router.register(r'payment', views.PaymentViewSet)
router.register(r'paymenttype', views.PaymentTypeViewSet)
# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]