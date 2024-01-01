from django.contrib import admin

# Register your models here.
from .models import Award, Member, AssessmentUnit, GradingResult, Class, Payment, PaymentType, GradingInvite

admin.site.register(Award)
admin.site.register(Member)
admin.site.register(AssessmentUnit)
admin.site.register(GradingResult)
admin.site.register(Class)
admin.site.register(Payment)
admin.site.register(PaymentType)
admin.site.register(GradingInvite)
