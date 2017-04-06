from django import forms
from . import models


class PatternForm(forms.ModelForm):
    class Meta:
        model = models.Pattern
        fields = ['pattern_label', 'pattern_text', 'extracted_elements_type']
