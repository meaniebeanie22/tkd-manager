from django.core.management.base import BaseCommand, CommandError
from dashboard.models import Payment, PaymentType, RecurringPayment, Member
from django.db.models import Q
import datetime

class Command(BaseCommand):
    def handle(self):
        affected = 0
        for rpayment in RecurringPayment.objects.filter(Q(next_due__lte=datetime.datetime.now()) | Q(last_payment_date__isnull=True)):
            # payments that need renewal
            p = rpayment.payments.create(member=rpayment.member, paymenttype=rpayment.paymenttype, amount_due=rpayment.amount)
            rpayment.last_payment_date = datetime.date.today()
            rpayment.save()
            affected += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully Recurred Payments.\nAffected {affected} RecurringPayments.')
        )

