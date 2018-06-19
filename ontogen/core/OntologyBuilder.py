import re

from .Ontology import Ontology
from ontogen.models import Pattern, FramesetGranule

from .constants import *


def get_node_number(ontology, node):
    for relation in ontology.out_relations(node):
        if relation['name'] == NUMBER_RELATION:
            return ontology.node_by_id(relation['destination_node_id'])['name']
    else:
        raise NameError()


def get_elements_by_type(elements, target_type):
    results = []
    for element in elements:
        try:
            if element['type'] == target_type:
                results.append(element)
        except KeyError:
            raise ValueError
    return results


def build_subject_ontology(elements):
    subject = Ontology()

    current_number = 1

    concepts = get_elements_by_type(elements, Pattern.CONCEPT)
    for concept in concepts:
        main_node = subject.add_node(NO_NAME_NODE)
        name_node = subject.add_node(concept['name'])
        number_node = subject.add_node(current_number)

        subject.add_relation(NAME_RELATION, main_node['id'], name_node['id'])
        subject.add_relation(NUMBER_RELATION, main_node['id'], number_node['id'])

        name_node['attributes'][MATCHED_TEXT_ATTR] = concept[MATCHED_TEXT_ATTR]
        current_number += 1

    return subject


def get_source_node_by_relation(ontology, node, relation_name):
    in_relations = Ontology.relations_as_dict(ontology.in_relations(node))
    return ontology.node_by_id(in_relations[relation_name]['source_node_id'])


def build_task_ontology(elements, subject_ont):
    subject = Ontology.from_json(subject_ont)
    task = Ontology()
    task_nodes = []

    prev_node = task.add_node('Начало')

    def find_node_by_matched_text(text):
        text = text.strip()

        for node in subject.nodes:
            attr = node['attributes']
            if MATCHED_TEXT_ATTR in attr and attr[MATCHED_TEXT_ATTR] == text:
                name_node = node
                break
        else:
            return None

        return get_source_node_by_relation(subject, name_node, 'name')

    relations = get_elements_by_type(elements, Pattern.RELATION)

    number_regex = re.compile(r' \((\d+)\)')

    def split_name_number(text):
        try:
            number = next(number_regex.finditer(text)).group(1)
        except StopIteration:
            number = None

        name = number_regex.sub('', text)

        return name, number

    for relation in relations:
        source_name, _ = split_name_number(relation['source'])
        destination_name, _ = split_name_number(relation['destination'])

        source_node = find_node_by_matched_text(source_name) \
            or find_node_by_matched_text(relation['source'])
        destination_node = find_node_by_matched_text(destination_name) \
            or find_node_by_matched_text(relation['destination'])

        try:
            if subject.get_relation_by_nodes(source_node, destination_node) is None:
                subject.add_relation(
                    relation['name'], source_node['id'], destination_node['id'])
        except TypeError:
            print('relation {0} at {1}: source or destination not found'.format(
                relation['applied_name'], relation[MATCH_START_ATTR]))
            continue

        if 'applied_name' not in relation:
            continue

        action = task.add_node(relation['applied_name'])
        from_node = task.add_node(get_node_number(subject, source_node))
        to_node = task.add_node(get_node_number(subject, destination_node))

        task.add_relation(
            'next', prev_node['id'], action['id']),
        task.add_relation(
            'from', action['id'], from_node['id']),
        task.add_relation(
            'to', action['id'], to_node['id'])

        prev_node = action
        task_nodes.append(action)

    end = task.add_node('Конец')
    task.add_relation(
        'next', prev_node['id'], end['id'])

    return task, subject, task_nodes


def populate_with_image(subject_ont, node_name, image):
    subject = Ontology.from_json(subject_ont)

    name_node = subject.node_by_name(node_name)
    main_node = get_source_node_by_relation(subject, name_node, 'name')

    image_node = subject.add_node("[image] " + node_name)
    image_node['attributes']['image_url'] = image

    subject.add_relation(IMAGE_RELATION, main_node['id'], image_node['id'])

    return subject


def populate_task_with_method(task_ont, step_index, method, resource):
    task = Ontology.from_json(task_ont)

    current_step = task.node_by_id(1)
    assert(current_step['name'] == "Начало")

    for i in range(int(step_index) + 1):
        relations = task.relations_as_dict(task.out_relations(current_step))
        current_step = task.node_by_id(relations['next']['destination_node_id'])

    method = task.add_node(method)
    task.add_relation_by_nodes('visualizer', current_step, method)

    match = re.match(r'(?P<type>\w+)(?P<id>\d+)', resource)
    resource_type = match.group('type')
    resource_id = match.group('id')

    if resource_type == "frameset":
        frameset = FramesetGranule.objects.get(pk=resource_id)
        frameset_node = task.add_node(frameset.name)
        frameset_node['attributes']['url'] = 'resources/framesets/{}'.format(frameset.id)
        task.add_relation_by_nodes('resource', current_step, frameset_node)

        first_frame = task.add_node(frameset.first_frame)
        task.add_relation_by_nodes('first_frame', frameset_node, first_frame)

        last_frame = task.add_node(frameset.last_frame)
        task.add_relation_by_nodes('last_frame', frameset_node, last_frame)
    else:
        raise NotImplementedError

    return task
