from django.contrib import admin
from rsem_report.models import GSE

class GSEAdmin(admin.ModelAdmin):
    pass

admin.site.register(GSE, GSEAdmin)
