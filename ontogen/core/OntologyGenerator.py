import os
import re
import json
from copy import deepcopy

from .Parser.PatternReader import PatternReader
from .Parser.PatternMatcher import PatternMatcher
from .OntoGen import OntoGen


def append_index(pattern, index):
    names = re.findall(r'P<(\w+)>', pattern['regex'])
    for name in names:
        index_name = '{0}_{1}'.format(name, index)
        pattern['regex'] = \
            pattern['regex'].replace(
                '<{}>'.format(name),
                '<{}>'.format(index_name)
            )
        pattern['mappings'] = \
            pattern['mappings'].replace(name, index_name)
    return pattern


def resolve_names(patterns):
    names_map = {pattern['name']: pattern for pattern in patterns}

    for pattern in patterns:
        dependencies = \
            re.findall(r'(?:\(\\s\*\)|\A)([A-Z]\w*)', pattern['regex'])
        for dependency in dependencies:
            d_split = dependency.split('_')
            if len(d_split) > 1:
                dependency_name = ''.join(d_split[:len(d_split) - 1])
                dependency_index = d_split[-1]
            else:
                dependency_name = d_split[0]
                dependency_index = None

            if dependency_name not in names_map:
                continue

            resolution = deepcopy(names_map[dependency_name])
            if dependency_index is not None:
                resolution = append_index(resolution, dependency_index)

            resolution_mapping = \
                re.findall(r'name=([^ ]+)', resolution['mappings'])
            if len(resolution_mapping) == 0:
                raise Exception(
                    'Dependency pattern does not contain "name" mapping')

            pattern['regex'] = \
                pattern['regex'].replace(dependency, resolution['regex'])
            pattern['mappings'] = \
                pattern['mappings'].replace(dependency, resolution_mapping[0])
    return patterns


def generate_ontologies_from_text(text, pattern_set=None):
    reader = PatternReader()
    matcher = PatternMatcher()
    builder = OntoGen()

    if pattern_set is None:
        patterns = reader.read(os.path.join(os.path.dirname(__file__),
                               'defaults/patterns'))
    else:
        patterns = [pattern.get() for pattern in pattern_set]

    patterns = resolve_names(patterns)

    matches = matcher.parse_text(text, patterns)
    builder.parse_elements(matches)
    return builder.get_subject_ontology(), builder.get_applied_ontology()


def generate_subject_ontology(text, pattern_set):
    reader = PatternReader()
    matcher = PatternMatcher()
    builder = OntoGen()

    patterns = [pattern.get() for pattern in pattern_set if pattern.extracted_elements_type == pattern.CONCEPT]
    patterns = resolve_names(patterns)

    matches = matcher.parse_text(text, patterns)
    builder.parse_elements(matches)
    return builder.get_subject_ontology()


def merge_ontologies(one, another):
    ont1 = json.loads(one)
    ont2 = json.loads(another)

    ontology = {
            "nodes": ont1['nodes'] + ont2['nodes'],
            "relations": ont1['relations'] + ont2['relations'],
            "namespaces": ont1['namespaces'],
            "last_id": str(max([int(ont1['last_id']), int(ont2['last_id'])])),
        }

    return json.dumps(ontology, ensure_ascii=False)
