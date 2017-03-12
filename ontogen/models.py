from django.db import models

from .core.Parser.PatternReader import PatternReader

class Instruction(models.Model):
    instruction_label = models.CharField(max_length=50)
    instruction_text = models.TextField()

    def __str__(self):
        return self.instruction_label

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
        return self.pattern_label + ' -> ' + \
            ', '.join([str(mapping) for mapping in self.mappings.all()]) #pylint: disable=E1101

    def get(self):
        reader = PatternReader()
        regex = reader.parse_pattern(self.pattern_text)
        pattern_mappings = ' '.join([mapping.get() for mapping in self.mappings.all()]) #pylint: disable=E1101
        pattern_mappings += ' type=' + self.extracted_elements_type

        return {'regex': regex, 'mappings': pattern_mappings}

class Mapping(models.Model):
    pattern = models.ForeignKey(Pattern, on_delete=models.CASCADE, related_name='mappings')
    mapping_label = models.CharField(max_length=50)
    mapping_value = models.CharField(max_length=100)

    def __str__(self):
        return self.mapping_label

    def get(self):
        return self.mapping_label + '=' + self.mapping_value

class GeneratorConfig(models.Model):
    instruction = models.ForeignKey(Instruction)
    patterns = models.ManyToManyField(Pattern)
