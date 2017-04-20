import json
import math


class InvalidDataError(Exception):
    def __init__(self):
        message = "Invalid data passed"
        super().__init__(message)


class OntoGen:
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
        self.current_id = 0
        self.current_n = 0
        self.relations = []
        self.nodes = []
        self.elements = []

    def get_next_id(self):
        self.current_id += 1
        return self.current_id

    def get_next_n(self):
        self.current_n += 1
        return self.current_n

    def get_node_id(self, target_name):
        for node in self.nodes:
            if node['name'] == target_name:
                return node['id']
        return None

    def get_node_by_id(self, node_id):
        for node in self.nodes:
            if node['id'] == node_id:
                return node
        return None

    def construct_node(self, name):
        return {
            'id': str(self.get_next_id()),
            'attributes': {},
            'namespace': self.default_namespace,
            'name': str(name),
        }

    def construct_relation(self, name, source, dest):
        return self.construct_relation_by_ids(
            name,
            self.get_node_id(source),
            self.get_node_id(dest))

    def construct_relation_by_ids(self, name, source_id, dest_id):
        base = self.construct_node(name)
        base.update({
            'source_node_id': str(source_id),
            'destination_node_id': str(dest_id),
        })
        return base

    def create_layout(self):
        radius = 250
        center = (radius + 50, radius + 50)
        if len(self.nodes) == 0:
            return

        angle_step = math.radians(360 / len(self.nodes))
        angle = math.radians(90)

        for item in self.nodes:
            item['position_x'] = \
                center[0] + math.floor(radius * math.cos(angle))
            item['position_y'] = \
                center[1] + math.floor(radius * math.sin(angle))
            angle += angle_step

    @staticmethod
    def get_elements_by_type(elements, target_type):
        results = []
        for element in elements:
            try:
                if element['type'] == target_type:
                    results.append(element)
            except KeyError:
                raise InvalidDataError()
        return results

    def parse_elements(self, elements):
        self.elements = elements
        concepts = self.get_elements_by_type(elements, 'concept')
        for concept in concepts:
            self.add_node_with_number(concept['name'])

        relations = self.get_elements_by_type(elements, 'relation')
        for rel in relations:
            if not self.get_node_id(rel['source']):
                self.add_node_with_number(rel['source'])
            if not self.get_node_id(rel['destination']):
                self.add_node_with_number(rel['destination'])

            self.relations.append(
                self.construct_relation(
                    rel['name'], rel['source'], rel['destination']))

    def add_node_with_number(self, concept_name):
        node = self.construct_node(concept_name)
        number_node = self.construct_node(self.get_next_n())
        self.nodes.extend([node, number_node])
        has_number_rel = self.construct_relation_by_ids(
            'has_number', node['id'], number_node['id'])
        self.relations.append(has_number_rel)

    def get_subject_ontology(self):
        self.create_layout()

        ontology = {
            "nodes": self.nodes,
            "relations": self.relations,
            "namespaces": self.ontology_namespaces,
            "last_id": str(self.current_id),
        }

        return json.dumps(ontology, ensure_ascii=False)  # , indent=4)

    def get_number_node(self, node_name):
        node_id = self.get_node_id(node_name)
        for rel in self.relations:
            if rel['name'] == 'has_number' \
                    and rel['source_node_id'] == node_id:
                return self.get_node_by_id(rel['destination_node_id'])

    @staticmethod
    def create_layout_applied(nodes):
        x = 1250
        y = 50

        nodes[0]['position_x'] = x
        nodes[0]['position_y'] = y
        y += 100

        count = (len(nodes) - 2) / 3
        for i in range(int(count)):
            idx = 3 * i + 1
            nodes[idx]['position_x'] = x
            nodes[idx]['position_y'] = y

            nodes[idx + 1]['position_x'] = x - 200
            nodes[idx + 1]['position_y'] = y

            nodes[idx + 2]['position_x'] = x + 200
            nodes[idx + 2]['position_y'] = y

            y += 100

        nodes[-1]['position_x'] = x
        nodes[-1]['position_y'] = y

        return nodes

    def get_applied_ontology(self):
        begin = self.construct_node('Начало')
        nodes = []
        relations = []
        nodes.append(begin)

        prev_node = begin
        relations_candidates = self.get_elements_by_type(self.elements, 'relation')
        for rel in relations_candidates:
            if 'applied_name' not in rel:
                continue

            action = self.construct_node(rel['applied_name'])
            from_node = self.construct_node(
                self.get_number_node(rel['source'])['name'])
            to_node = self.construct_node(
                self.get_number_node(rel['destination'])['name'])

            nodes.extend(
                [action, from_node, to_node]
            )
            relations.extend([
                self.construct_relation_by_ids(
                    'next', prev_node['id'], action['id']),
                self.construct_relation_by_ids(
                    'from', from_node['id'], action['id']),
                self.construct_relation_by_ids(
                    'to', action['id'], to_node['id'])
            ])

            prev_node = action
        end = self.construct_node('Конец')
        nodes.append(end)
        relations.append(
            self.construct_relation_by_ids(
                    'next', prev_node['id'], end['id'])
        )

        ontology = {
            "nodes": self.create_layout_applied(nodes),
            "relations": relations,
            "namespaces": self.ontology_namespaces,
            "last_id": str(self.current_id),
        }

        return json.dumps(ontology, ensure_ascii=False)  # , indent=4)
