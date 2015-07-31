from django.contrib import admin
from rsemreport.models import GSE, Species, GSM

class GSEAdmin(admin.ModelAdmin):
    def get_num_gsms(self, obj):
        return obj.gsm_set.count()
    get_num_gsms.short_description = 'number of GSMs'
    
    list_display = ['name', 'get_num_gsms', 'created', 'updated']
    readonly_fields = ['created', 'updated']
    search_fields = ('name',)


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

    list_display = ('name', 'status', 'get_gse', 'get_species', 'created', 'updated')
    ordering = ('gse__name', 'name')
    search_fields = ('name',)

    readonly_fields = ('created', 'updated')



admin.site.register(GSE, GSEAdmin)
admin.site.register(Species, SpeciesAdmin)
admin.site.register(GSM, GSMAdmin)
