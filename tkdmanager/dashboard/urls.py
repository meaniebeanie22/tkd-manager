from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.MemberListView.as_view(), name='members'),
    path('member/<int:pk>', views.MemberDetailView.as_view(), name='member-detail'),
    path('grading-result/<int:pk>', views.GradingResultDetailView.as_view(), name='grading-result-detail'),
    path('member/create', views.MemberCreate.as_view(), name='add-member'),
    path('member/<int:pk>/update', views.MemberUpdate.as_view(), name='update-member'),
    path('grading-result/<int:pk>/update', views.manageGradingResult, name='update-grading-result'),
]