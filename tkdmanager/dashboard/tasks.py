from .models import RecurringPayment
from django.db.models import Q
from celery import shared_task
from django.utils import timezone


@shared_task
def recurpayments():
    print("Beginning to recur payments.")
    affected = 0
    for rpayment in RecurringPayment.objects.filter(
        Q(next_due__lte=timezone.now()) | Q(last_payment_date__isnull=True)
    ):
        # payments that need renewal
        p = rpayment.payments.create(
            member=rpayment.member,
            paymenttype=rpayment.paymenttype,
            amount_due=rpayment.amount,
        )
        rpayment.last_payment_date = timezone.now().date()
        rpayment.save()
        affected += 1
    print(f"Successfully Recurred Payments.\nAffected {affected} RecurringPayments.")
