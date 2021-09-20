from django.contrib import admin
from .models import Source, UserIncome
# Register your models here.
class IncomeeAdmin(admin.ModelAdmin):
    list_display = ('amount','description','owner','source','date',)
    search_fields = ('description','category','date',)
    list_per_page = 5
admin.site.register(UserIncome)
admin.site.register(Source)
