from django.core.management.base import BaseCommand, CommandError
from dashboard.models import Payment, PaymentType, RecurringPayment, Member
import datetime

class Command(BaseCommand):
    def handle(self):
        for rpayment in RecurringPayment.objects.filter(next_due__lte=datetime.datetime.now()):
            # payments that need renewal
            p = rpayment.payments.create(member=rpayment.member, paymenttype=rpayment.paymenttype, amount_due=rpayment.amount)
            rpayment.last_payment_date = datetime.date.today()
            rpayment.save()

