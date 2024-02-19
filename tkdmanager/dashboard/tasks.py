from .models import RecurringPayment
from django.db.models import Q
from tkdmanager.celery import app
import datetime

@app.task
def recurpayments():
    print("Beginning to recur payments.")
    affected = 0
    for rpayment in RecurringPayment.objects.filter(Q(next_due__lte=datetime.datetime.now()) | Q(last_payment_date__isnull=True)):
        # payments that need renewal
        p = rpayment.payments.create(member=rpayment.member, paymenttype=rpayment.paymenttype, amount_due=rpayment.amount)
        rpayment.last_payment_date = datetime.date.today()
        rpayment.save()
        affected += 1
    print(f'Successfully Recurred Payments.\nAffected {affected} RecurringPayments.')