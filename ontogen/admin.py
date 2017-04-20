from django.forms import models
from django.contrib import admin
from django.core.exceptions import ValidationError

from .models import Pattern, Mapping, Instruction, HistoryRecord, Ontology


class MappingInlineFormset(models.BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.is_valid():
                return
            label = form.cleaned_data.get('mapping_label')
            if not form.cleaned_data.get('DELETE') and \
               (label == 'name' or label == 'applied_name'):
                break
        else:
            raise ValidationError("'Name' mapping should be provided")


class MappingInline(admin.TabularInline):
    formset = MappingInlineFormset
    model = Mapping
    extra = 1


class PatternAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields':
                ['pattern_label', 'pattern_text', 'extracted_elements_type']})
    ]
    inlines = [MappingInline]

    class Media:
        css = {
            'all': ('ontogen/custom_admin.css',)
        }

admin.site.register(Instruction)
admin.site.register(Pattern, PatternAdmin)
admin.site.register(HistoryRecord)
admin.site.register(Ontology)
