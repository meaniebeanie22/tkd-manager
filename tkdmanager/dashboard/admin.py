from django.contrib import admin

# Register your models here.
from .models import (AssessmentUnit, Award, Class, Grading, GradingInvite,
                     GradingResult, Member, Payment, PaymentType,
                     RecurringPayment)

admin.site.register(Award)
admin.site.register(Member)
admin.site.register(AssessmentUnit)
admin.site.register(GradingResult)
admin.site.register(Class)
admin.site.register(Payment)
admin.site.register(PaymentType)
admin.site.register(GradingInvite)
admin.site.register(Grading)
admin.site.register(RecurringPayment)