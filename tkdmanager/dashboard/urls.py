from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('members/', views.MemberListView.as_view(), name='members'),
    path('member/<int:pk>', views.MemberDetailView.as_view(), name='member-detail'),
]