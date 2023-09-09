from django.contrib import admin

# Register your models here.
from .models import Belt, Award

admin.site.register(Belt)
admin.site.register(Award)
