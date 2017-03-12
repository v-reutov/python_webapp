from django.contrib import admin

from .models import Pattern, Mapping, Instruction

# Register your models here.
class MappingInline(admin.TabularInline):
    model = Mapping
    extra = 1

class PatternAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['pattern_label', 'pattern_text', 'extracted_elements_type']})
    ]
    inlines = [MappingInline]

    class Media:
        css = {
            'all' : ('ontogen/custom_admin.css',)
        }

admin.site.register(Instruction)
admin.site.register(Pattern, PatternAdmin)
