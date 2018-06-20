import re
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ugettext
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType

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

    @classmethod
    def get_json_all(cls):
        return {
            "text": ugettext("Instructions"),
            "type": "instruction-container",
            "children": [
                item.get_json() for item in Instruction.objects.all()
            ],
            "li_attr": {
                "class": "select-single capitalized container"
            }
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

    MAPPING_SEPARATOR = ';;;'

    extracted_elements_type = \
        models.CharField(
            _("extracted elements type"), max_length=50,
            choices=ELEMENT_TYPES, default=CONCEPT)

    def __str__(self):
        return self.pattern_label

    def get(self):
        reader = PatternReader()
        regex = reader.parse_pattern(self.pattern_text)
        pattern_mappings = self.MAPPING_SEPARATOR.join(
            [mapping.get() for mapping in self.mappings.all()])
        if self.extracted_elements_type is not None:
            pattern_mappings += self.MAPPING_SEPARATOR \
                + 'type=' + self.extracted_elements_type
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

    @classmethod
    def get_json_all(cls):
        return {
            "text": ugettext("Patterns"),
            "type": "pattern-container",
            "children": [
                item.get_json() for item in Pattern.objects.all()
            ],
            "li_attr": {
                "class": "select-multiple capitalized container"
            }
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


class AbstractGranule(models.Model):
    name = models.CharField(max_length=200)
    # meta_data = JSONField()

    CONTAINER_TYPE = 'cont'
    TERMINAL_TYPE = 'term'

    GRANULE_TYPES = (
        (None, '-'),
        (CONTAINER_TYPE, _('Container')),
        (TERMINAL_TYPE, _('Terminal')),
    )

    type = models.CharField(max_length=4, choices=GRANULE_TYPES, default=TERMINAL_TYPE)

    child_granules = models.ManyToManyField("self")

    class Meta:
        abstract = True

    def get_elements(self):
        if self.type == self.TERMINAL_TYPE:
            return [str(x) for x in self.elements.all()]
        else:  # self is a container
            elements = []

            for child in self.child_granules.all():
                elements.append(child.get_elements())

            return elements

    def __str__(self):
        return self.name


class GranuleItem(models.Model):
    url = models.CharField(max_length=200)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    granule = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.url


class FramesetGranule(AbstractGranule):
    first_frame = models.CharField(max_length=200)
    last_frame = models.CharField(max_length=200)

    elements = GenericRelation(GranuleItem)

    def to_json(self):
        return {
            'first': self.first_frame,
            'last': self.last_frame,
            'elements': self.get_elements()
        }

    def get_tree_json(self):
        return {
            "id": "frameset" + str(self.id),
            "type": "frameset",
            "text": str(self),
        }

    @classmethod
    def get_tree_json_all(cls):
        return {
            "text": ugettext("Framesets"),
            "type": "frameset-container",
            "children": [
                item.get_tree_json() for item in cls.objects.all()
            ],
            "li_attr": {
                "class": "select-multiple capitalized container"
            }
        }
