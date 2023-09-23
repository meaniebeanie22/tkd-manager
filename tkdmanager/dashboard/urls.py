from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.MemberListView.as_view(), name='members'),
    path('member/<int:pk>', views.MemberDetailView.as_view(), name='member-detail'),
    path('grading-result/<int:pk>', views.GradingResultDetailView.as_view(), name='grading-result-detail'),
    path('member/create', views.MemberCreate.as_view(), name='add-member'),
    path('member/<int:pk>/update', views.MemberUpdate.as_view(), name='update-member'),
    path('member/<int:pk>/delete', views.MemberDelete.as_view(), name='delete-member'),
    path('grading-result/create', views.GradingResultCreate.as_view(), name='add-grading-result'),
    path('grading-result/<int:pk>/update', views.GradingResultUpdate.as_view(), name='update-grading-result'),
    path('grading-result/<int:pk>/update2', views.manageGradingResult, name='update-grading-result2'),
    path('grading-result/<int:pk>/delete', views.GradingResultDelete.as_view(), name='delete-grading-result'),
    path('gradings/', views.GradingResultListView.as_view(), name='gradingresults'),
    path('awards/', views.AwardListView.as_view(), name='awards'),
    path('award/<int:pk>/update', views.AwardUpdate.as_view(), name='update-award'),
    path('award/create', views.AwardCreate.as_view(), name='add-award'),
    path('award/<int:pk>', views.AwardDetailView.as_view(), name='award-detail'),
]