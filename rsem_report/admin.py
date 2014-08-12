from django.contrib import admin
from rsem_report.models import GSE, Species, GSM

class GSEAdmin(admin.ModelAdmin):
    list_display = ['name']
    readonly_fields = ['created', 'updated']

class SpeciesAdmin(admin.ModelAdmin):
    list_display = ['name']


class GSMAdmin(admin.ModelAdmin):
    def get_gse(self, obj):
        return obj.gse.name
    get_gse.short_description = 'GSE'
    get_gse.admin_order_field = 'gse__name'

    def get_species(self, obj):
        return obj.species.name
    get_species.short_description = 'Species'
    get_species.admin_order_field = 'species__name'

    list_display = ['name', 'status', 'get_gse', 'get_species']

    readonly_fields = ['created', 'updated']



admin.site.register(GSE, GSEAdmin)
admin.site.register(Species, SpeciesAdmin)
admin.site.register(GSM, GSMAdmin)
