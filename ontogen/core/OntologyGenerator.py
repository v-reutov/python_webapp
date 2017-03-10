import os

from .Parser.PatternReader import PatternReader
from .Parser.PatternMatcher import PatternMatcher
from .OntologyBuilder.OntologyBuilder import OntologyBuilder

def generate_ontology_from_text(text):
    reader = PatternReader()
    matcher = PatternMatcher()
    builder = OntologyBuilder()

    patterns = reader.read(os.path.join(os.path.dirname(__file__), 'defaults/patterns'))
    matches = matcher.parse_text(text, patterns)
    return builder.build_ontology(matches)
