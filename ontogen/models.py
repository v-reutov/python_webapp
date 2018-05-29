import re
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

from .core.Parser.PatternReader import PatternReader


class Instruction(models.Model):
    instruction_label = models.CharField(_("instruction label"), max_length=50)
    instruction_text = models.TextField(_("instruction text"))
    
    instruction_content = RichTextField(_("instruction content"), default='')

    def __str__(self):
        return self.instruction_label

    def get_json(self):
        return {
            "id": "instruction" + str(self.id),
            "type": "instruction",
            "text": str(self),
        }


class Pattern(models.Model):
    pattern_label = models.CharField(_("pattern label"), max_length=50)
    pattern_text = models.CharField(_("pattern text"), max_length=200)

    NONE = None
    CONCEPT = 'concept'
    RELATION = 'relation'
    ELEMENT_TYPES = (
        (NONE, '-'),
        (CONCEPT, _('Concept')),
        (RELATION, _('Relation')),
    )

    extracted_elements_type = \
        models.CharField(
            _("extracted elements type"), max_length=50,
            choices=ELEMENT_TYPES, default=CONCEPT)

    def __str__(self):
        return self.pattern_label

    def get(self):
        reader = PatternReader()
        regex = reader.parse_pattern(self.pattern_text)
        pattern_mappings = ' '.join(
            [mapping.get() for mapping in self.mappings.all()])
        if self.extracted_elements_type is not None:
            pattern_mappings += ' type=' + self.extracted_elements_type
        return {
            'name': self.pattern_label,
            'regex': regex,
            'mappings': pattern_mappings}

    def get_json(self):
        return {
            "id": "pattern" + str(self.id),
            "type": "pattern",
            "text": str(self)
        }


class Mapping(models.Model):
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE,
                                related_name='mappings')
    mapping_label = models.CharField(_("mapping label"), max_length=50)
    mapping_value = models.CharField(_("mapping value"), max_length=100)

    def __str__(self):
        return self.mapping_label.replace('_', ' ')

    def get(self):
        return self.mapping_label + '=' + self.mapping_value


class Ontology(models.Model):
    name = models.CharField(_("ontology name"), max_length=50)
    ont = models.TextField()

    SUBJECT = 'subject'
    APPLIED = 'applied'
    ONTOLOGY_TYPES = (
        (SUBJECT, _('subject ontology')),
        (APPLIED, _('applied ontology')),
    )

    ontology_type = \
        models.CharField(
            _("ontology type"), max_length=50,
            choices=ONTOLOGY_TYPES)


class HistoryRecord(models.Model):
    datetime = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User)
    instruction = models.ForeignKey(Instruction)
    patterns = models.ManyToManyField(Pattern)
    results = models.ManyToManyField(Ontology)

    def __str__(self):
        return '[' + str(self.datetime) + '] ' + self.user.username

    class Meta:
        ordering = ('datetime', 'user')


def get_instructions():
    return {
        "text": ugettext("Instructions"),
        "type": "instruction-container",
        "children": [
            item.get_json() for item in Instruction.objects.all()
        ],
        "li_attr": {
            "class": "select-single capitalized"
        }
    }


def get_patterns():
    return {
        "text": ugettext("Patterns"),
        "type": "pattern-container",
        "children": [
            item.get_json() for item in Pattern.objects.all()
        ],
        "li_attr": {
            "class": "select-multiple capitalized"
        }
    }

def get_multimedia_data():
    return {
        "text": ugettext("Multimedia data"),
        "type": "pattern-container",
        "children": [
            {
                "id": "obj1",
                "type": "data",
                "text": "test2"
            },
            {
                "id": "obj2",
                "type": "data",
                "text": "test3"
            }
        ],
        "li_attr": {
            "class": "select-multiple capitalized"
        }
    }


def get_resources():
    return {
        "text": ugettext("Resources"),
        "type": "resource-root",
        "children": [
            get_instructions(),
            get_patterns(),
            get_multimedia_data(),
        ],
        "li_attr": {
            "class": "capitalized"
        }
    }
