import os

from .Parser.PatternReader import PatternReader
from .Parser.PatternMatcher import PatternMatcher
from .OntologyBuilder.OntologyBuilder import OntologyBuilder

def generate_ontology_from_text(text, pattern_set=None):
    reader = PatternReader()
    matcher = PatternMatcher()
    builder = OntologyBuilder()

    if pattern_set is None:
        patterns = reader.read(os.path.join(os.path.dirname(__file__), 'defaults/patterns'))
    else:
        patterns = [pattern.get() for pattern in pattern_set]

    matches = matcher.parse_text(text, patterns)
    return builder.build_ontology(matches)
