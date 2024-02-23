from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="dash-index"),
    path("members", views.MemberListView.as_view(), name="dash-members"),
    path(
        "member/detail/<str:pk>",
        views.MemberDetailView.as_view(),
        name="dash-member-detail",
    ),
    path(
        "grading-result/detail/<str:pk>",
        views.GradingResultDetailView.as_view(),
        name="dash-grading-result-detail",
    ),
    path("member/create", views.MemberCreate.as_view(), name="dash-add-member"),
    path(
        "member/<str:pk>/update",
        views.MemberUpdate.as_view(),
        name="dash-update-member",
    ),
    path(
        "member/<str:pk>/delete",
        views.MemberDelete.as_view(),
        name="dash-delete-member",
    ),
    path(
        "member/<str:pk>/get-details",
        views.MemberGetDetails.as_view(),
        name="dash-member-get-details",
    ),
    path(
        "grading-result/create",
        views.GradingResultCreate.as_view(),
        name="dash-add-grading-result",
    ),
    path(
        "grading-result/<str:pk>/update",
        views.GradingResultUpdate.as_view(),
        name="dash-update-grading-result",
    ),
    path(
        "grading-result/<str:pk>/update2",
        views.manageGradingResult,
        name="dash-update-grading-result2",
    ),
    path(
        "grading-result/<str:pk>/update3",
        views.manageGradingResultLetter,
        name="dash-update-grading-result3",
    ),
    path(
        "grading-result/<str:pk>/delete",
        views.GradingResultDelete.as_view(),
        name="dash-delete-grading-result",
    ),
    path(
        "grading-results",
        views.GradingResultListView.as_view(),
        name="dash-gradingresults",
    ),
    path("awards", views.AwardListView.as_view(), name="dash-awards"),
    path(
        "award/<str:pk>/update", views.AwardUpdate.as_view(), name="dash-update-award"
    ),
    path("award/create", views.AwardCreate.as_view(), name="dash-add-award"),
    path(
        "award/detail/<str:pk>",
        views.AwardDetailView.as_view(),
        name="dash-award-detail",
    ),
    path(
        "award/<str:pk>/delete", views.AwardDelete.as_view(), name="dash-delete-award"
    ),
    path("classes", views.ClassListView.as_view(), name="dash-classes"),
    path(
        "class/detail/<str:pk>",
        views.ClassDetailView.as_view(),
        name="dash-class-detail",
    ),
    path("class/create", views.ClassCreate.as_view(), name="dash-add-class"),
    path(
        "class/<str:pk>/update", views.ClassUpdate.as_view(), name="dash-update-class"
    ),
    path(
        "class/<str:pk>/delete", views.ClassDelete.as_view(), name="dash-delete-class"
    ),
    path("payments/", views.PaymentListView.as_view(), name="dash-payments"),
    path(
        "payment/detail/<str:pk>",
        views.PaymentDetailView.as_view(),
        name="dash-payment-detail",
    ),
    path("payment/create", views.PaymentCreate.as_view(), name="dash-add-payment"),
    path(
        "payment/<str:pk>/update",
        views.PaymentUpdate.as_view(),
        name="dash-update-payment",
    ),
    path(
        "payment/<str:pk>/delete",
        views.PaymentDelete.as_view(),
        name="dash-delete-payment",
    ),
    path(
        "payment-type/<str:pk>/get_standard_amount",
        views.GetStandardAmountView.as_view(),
        name="dash-payment-get-standard-amount",
    ),
    path(
        "payment-type/create",
        views.PaymentTypeCreate.as_view(),
        name="dash-add-payment-type",
    ),
    path(
        "payment-type/<str:pk>/update",
        views.PaymentTypeUpdate.as_view(),
        name="dash-update-payment-type",
    ),
    path(
        "payment-types", views.PaymentTypeListView.as_view(), name="dash-payment-types"
    ),
    path(
        "payment-type/detail/<str:pk>",
        views.PaymentTypeDetailView.as_view(),
        name="dash-payment-type-detail",
    ),
    path(
        "payment-type/<str:pk>/delete",
        views.PaymentTypeDelete.as_view(),
        name="dash-delete-payment-type",
    ),
    path(
        "grading-invite/<str:pk>/download",
        views.gradinginvite_pdf_view,
        name="dash-grading-invite-download",
    ),
    path(
        "grading-invite/detail/<str:pk>",
        views.GradingInviteDetailView.as_view(),
        name="dash-grading-invite-detail",
    ),
    path(
        "grading-invites",
        views.GradingInviteListView.as_view(),
        name="dash-gradinginvites",
    ),
    path(
        "grading-invite/<str:pk>/update",
        views.GradingInviteUpdate.as_view(),
        name="dash-update-grading-invite",
    ),
    path(
        "grading-invite/create",
        views.GradingInviteCreate.as_view(),
        name="dash-add-grading-invite",
    ),
    path(
        "grading-invite/<str:pk>/delete",
        views.GradingInviteDelete.as_view(),
        name="dash-delete-grading-invite",
    ),
    path(
        "grading-invite/<str:pk>/get_details",
        views.GetGradingInviteDetailView.as_view(),
        name="dash-grading-invite-get-details",
    ),
    path(
        "member/<str:pk>/get_grading_invites",
        views.MemberGetGradingInvites.as_view(),
        name="dash-member-get-grading-invites",
    ),
    path(
        "member/<str:pk>/get_payments",
        views.MemberGetPayments.as_view(),
        name="dash-member-get-payments",
    ),
    path("gradings", views.GradingListView.as_view(), name="dash-gradings"),
    path("gradings-json", views.GetGradingsJSON.as_view(), name="dash-gradings-json"),
    path(
        "grading/detail/<str:pk>",
        views.GradingDetailView.as_view(),
        name="dash-grading-detail",
    ),
    path(
        "grading/<str:pk>/update",
        views.GradingUpdate.as_view(),
        name="dash-update-grading",
    ),
    path(
        "grading/<str:pk>/delete",
        views.GradingDelete.as_view(),
        name="dash-delete-grading",
    ),
    path("grading/create", views.GradingCreate.as_view(), name="dash-add-grading"),
    path(
        "gradingresult/<str:pk>/download",
        views.gradingresult_pdf_view,
        name="dash-grading-result-download",
    ),
    path("token", views.token_display, name="dash-get-token"),
    path("token/delete", views.token_delete, name="dash-delete-token"),
    path(
        "gradinginvite/batchdownload",
        views.gradinginvite_batch_pdf_view,
        name="dash-batch-generate-gi-pdf",
    ),
    path(
        "gradingresult/batchdownload",
        views.gradingresult_batch_pdf_view,
        name="dash-batch-generate-gr-pdf",
    ),
    path(
        "gradinginvite/batch_create",
        views.gradinginvite_batch_create,
        name="dash-batch-add-grading-invite",
    ),
    path(
        "gradinginvite/batch_create/review",
        views.batch_gradinginvite_revise,
        name="dash-batch-revise-grading-invite",
    ),
    path(
        "gradingresult/batchemail",
        views.gradingresult_batch_email_view,
        name="dash-batch-email-gr-pdf",
    ),
    path(
        "gradinginvite/batchemail",
        views.gradinginvite_batch_email_view,
        name="dash-batch-email-gi-pdf",
    ),
    path(
        "recurringpayment/detail/<str:pk>",
        views.RecurringPaymentDetailView.as_view(),
        name="dash-rpayment-detail",
    ),
    path(
        "recurringpayments",
        views.RecurringPaymentListView.as_view(),
        name="dash-rpayments",
    ),
    path(
        "recurringpayment/create",
        views.RecurringPaymentCreate.as_view(),
        name="dash-add-rpayment",
    ),
    path(
        "recurringpayment/<str:pk>/update",
        views.RecurringPaymentUpdate.as_view(),
        name="dash-update-rpayment",
    ),
    path(
        "recurringpayment/<str:pk>/delete",
        views.RecurringPaymentDelete.as_view(),
        name="dash-delete-rpayment",
    ),
    path("belts", views.manageBelts, name="dash-belts"),
    path("style/<str:pk>", views.selectStyle, name="dash-select-style"),
    path("styles", views.manageStyles, name="dash-styles"),
    path(
        "assessableunits", views.manageAssessmentUnitTypes, name="dash-assessableunits"
    ),
]
