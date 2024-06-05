from django.contrib import admin
from contact.models import contactform

class contactadmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message')


admin.site.register(contactform, contactadmin)
# Register your models here.
