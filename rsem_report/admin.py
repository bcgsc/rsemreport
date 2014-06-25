from django.contrib import admin
from rsem_report.models import GSE

class GSEAdmin(admin.ModelAdmin):
    list_display = ['name']
    readonly_fields = ['created', 'updated']

admin.site.register(GSE, GSEAdmin)
