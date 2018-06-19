import json
import math


class OntologyBuilder:
    def __init__(self):
        self.default_namespace = ""
        self.ontology_namespaces = {
            "default": self.default_namespace,
            "ontolis-avis": "http://knova.ru/ontolis-avis",
            "owl": "http://www.w3.org/2002/07/owl",
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema",
            "xsd": "http://www.w3.org/2001/XMLSchema"
        }

    def build_ontology(self, elements):
        concepts, relations = self.extract_concepts_and_relations(elements)
        concepts, relations = self.add_default_fields(concepts, relations)
        last_id = self.get_last_id(concepts, relations)

        concepts = self.create_layout(concepts)
        ontology = {
            "last_id": str(last_id),
            "namespaces": self.ontology_namespaces,
            "nodes": concepts,
            "relations": relations
        }
        return json.dumps(ontology, indent=4, ensure_ascii=False)

    def add_default_fields(self, *args):
        for arg in args:
            for item in arg:
                item['namespace'] = self.default_namespace
                item['attributes'] = {}
        return args

    @staticmethod
    def get_last_id(*args):
        last_id = -1
        for arg in args:
            for item in arg:
                if int(item['id']) > last_id:
                    last_id = int(item['id'])
        return last_id

    @staticmethod
    def create_layout(concepts):
        center = (100, 100)
        radius = 50
        angle_step = math.radians(360 / len(concepts))
        angle = math.radians(90)

        for item in concepts:
            item['position_x'] = math.cos(angle)
            item['position_y'] = math.sin(angle)
            angle += angle_step
        return concepts

    def extract_concepts_and_relations(self, elements):
        concepts_candidates = \
            self.extract_elements_by_type(elements, 'concept')
        relations = []
        concepts = []
        element_id = 0
        concept_id = 0
        for c_candidate in concepts_candidates:
            element_id += 1
            concepts.append(
                {'id': str(element_id), 'name': c_candidate['name']})
            concept_id += 1
            element_id += 1
            concepts.append({'id': str(element_id), 'name': str(concept_id)})
            element_id += 1
            relations.append({'id': str(element_id),
                              'name': 'has_number',
                              'source_node_id': str(element_id - 2),
                              'destination_node_id':  str(element_id - 1)})
        relation_candidates = \
            self.extract_elements_by_type(elements, 'relation')
        for r_candidate in relation_candidates:
            element_id += 1
            relations.append({
                'id': str(element_id),
                'name': 'a_part_of',  # r_candidate['relation'],
                'source_node_id':
                    self.get_concept_id(concepts, r_candidate['source']),
                'destination_node_id':
                    self.get_concept_id(concepts, r_candidate['destination'])
            })
        return concepts, relations

    @staticmethod
    def extract_elements_by_type(elements, target_type):
        results = []
        for element in elements:
            try:
                if element['type'] == target_type:
                    target = element.copy()
                    target.pop('type')
                    results.append(target)
            except KeyError:
                raise Exception('Invalid elements passed')
        return results

    @staticmethod
    def get_concept_id(concepts, target):
        for concept in concepts:
            if concept['name'] == target:
                return concept['id']
        return None
