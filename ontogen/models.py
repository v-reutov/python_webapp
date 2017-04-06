from django.db import models

from .core.Parser.PatternReader import PatternReader


class Instruction(models.Model):
    instruction_label = models.CharField(max_length=50)
    instruction_text = models.TextField()

    def __str__(self):
        return self.instruction_label

    def get_json(self):
        return {
            "id": "instruction" + str(self.id),
            "type": "instruction",
            "text": str(self)
        }


class Pattern(models.Model):
    pattern_label = models.CharField(max_length=50)
    pattern_text = models.CharField(max_length=200)

    CONCEPT = 'concept'
    RELATION = 'relation'
    ELEMENT_TYPES = (
        (CONCEPT, 'Concept'),
        (RELATION, 'Relation'),
    )

    extracted_elements_type = \
        models.CharField(max_length=50, choices=ELEMENT_TYPES, default=CONCEPT)

    def __str__(self):
        return self.pattern_label

    def get(self):
        reader = PatternReader()
        regex = reader.parse_pattern(self.pattern_text)
        pattern_mappings = ' '.join(
            [mapping.get() for mapping in self.mappings.all()])
        pattern_mappings += ' type=' + self.extracted_elements_type
        return {'regex': regex, 'mappings': pattern_mappings}

    def get_json(self):
        return {
            "id": "pattern" + str(self.id),
            "type": "pattern",
            "text": str(self)
        }


class Mapping(models.Model):
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE,
                                related_name='mappings')
    mapping_label = models.CharField(max_length=50)
    mapping_value = models.CharField(max_length=100)

    def __str__(self):
        return self.mapping_label.replace('_', ' ')

    def get(self):
        return self.mapping_label + '=' + self.mapping_value


class GeneratorConfig(models.Model):
    instruction = models.ForeignKey(Instruction)
    patterns = models.ManyToManyField(Pattern)


def get_instructions():
    return {
        "text": "Instructions",
        "type": "instruction-container",
        "children": [
            item.get_json() for item in Instruction.objects.all()
        ],
        "li_attr": {
            "class": "select-single"
        }
    }


def get_patterns():
    return {
        "text": "Patterns",
        "type": "pattern-container",
        "children": [
            item.get_json() for item in Pattern.objects.all()
        ],
        "li_attr": {
            "class": "select-multiple"
        }
    }


def get_resources():
    return {
        "text": "Resources",
        "type": "resource-root",
        "children": [
            get_instructions(),
            get_patterns()
        ]
    }
