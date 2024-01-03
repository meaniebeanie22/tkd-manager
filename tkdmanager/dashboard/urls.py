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
    path('member/<int:pk>/get-details', views.MemberGetDetails.as_view(), name='member-get-details'),
    path('grading-result/create', views.GradingResultCreate.as_view(), name='add-grading-result'),
    path('grading-result/<int:pk>/update', views.GradingResultUpdate.as_view(), name='update-grading-result'),
    path('grading-result/<int:pk>/update2', views.manageGradingResult, name='update-grading-result2'),
    path('grading-result/<int:pk>/update3', views.manageGradingResultLetter, name='update-grading-result3'),
    path('grading-result/<int:pk>/delete', views.GradingResultDelete.as_view(), name='delete-grading-result'),
    path('grading-results/', views.GradingResultListView.as_view(), name='gradingresults'),
    path('awards/', views.AwardListView.as_view(), name='awards'),
    path('award/<int:pk>/update', views.AwardUpdate.as_view(), name='update-award'),
    path('award/create', views.AwardCreate.as_view(), name='add-award'),
    path('award/<int:pk>', views.AwardDetailView.as_view(), name='award-detail'),
    path('award/<int:pk>/delete', views.AwardDelete.as_view(), name='delete-award'),
    path('classes/', views.ClassListView.as_view(), name='classes'),
    path('class/<int:pk>', views.ClassDetailView.as_view(), name='class-detail'),
    path('class/create', views.ClassCreate.as_view(), name='add-class'),
    path('class/<int:pk>/update', views.ClassUpdate.as_view(), name='update-class'),
    path('class/<int:pk>/delete', views.ClassDelete.as_view(), name='delete-class'),
    path('payments/', views.PaymentListView.as_view(), name='payments'),
    path('payment/<int:pk>', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('payment/create', views.PaymentCreate.as_view(), name='add-payment'),
    path('payment/<int:pk>/update', views.PaymentUpdate.as_view(), name='update-payment'),
    path('payment/<int:pk>/delete', views.PaymentDelete.as_view(), name='delete-payment'),
    path('paymenttype/<int:pk>/get_standard_amount', views.GetStandardAmountView.as_view(), name='payment-get-standard-amount'),
    path('gradinginvite/<int:pk>/download/', views.pdf_view, name='grading-invite-download'),
    path('gradinginvite/<int:pk>/', views.GradingInviteDetailView.as_view(), name='grading-invite-detail'),
    path('gradinginvites/', views.GradingInviteListView.as_view(), name='gradinginvites'),
    path('gradinginvite/<int:pk>/update/', views.GradingInviteUpdateView.as_view(), name='update-grading-invite'),
    path('gradinginvite/create/', views.GradingInviteCreateView.as_view(), name='add-grading-invite'),
    path('gradinginvite/<int:pk>/delete/', views.GradingInviteDeleteView.as_view(), name='delete-grading-invite'),
    path('gradinginvite/<int:pk>/get_details/', views.GetGradingInviteDetailView.as_view(), name='grading-invite-get-details'),
    path('member/<int:pk>/get_grading_invites/', views.MemberGetGradingInvites.as_view(), name='member-get-grading-invites'),
    path('member/<int:pk>/get_payments/', views.MemberGetPayments.as_view(), name='member-get-payments'),
    path('gradings/', views.GradingListView.as_view(), name='gradings'),
    path('grading/<int:pk>/', views.GradingDetailView.as_view(), name='grading-detail'),
    path('grading/<int:pk>/update/', views.GradingUpdateView.as_view(), name='update-grading'),
    path('grading/<int:pk>/delete/', views.GradingDeleteView.as_view(), name='delete-grading'),
    path('grading/create/', views.GradingCreateView.as_view(), name='add-grading'),
]