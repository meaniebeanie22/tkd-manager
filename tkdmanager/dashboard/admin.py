from django.contrib import admin

# Register your models here.
from .models import *
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
admin.site.register(MemberPropertyType)
admin.site.register(MemberProperty)
admin.site.register(Belt)
admin.site.register(AssessmentUnitType)
admin.site.register(ClassType)
admin.site.register(GradingType)
admin.site.register(Style)