from django.contrib import admin

# Register your models here.
from .models import Award, Member, AssessmentUnit, GradingResult

admin.site.register(Award)
admin.site.register(Member)
admin.site.register(AssessmentUnit)
admin.site.register(GradingResult)
