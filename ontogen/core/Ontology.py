import json


class Ontology:
    def __init__(self):
        self.nodes = []
        self.relations = []
        self.raw_data = {}

        self.last_id = 0
        self.default_namespace = ""

        self.tag = ""

    @classmethod
    def from_json(cls, json_data):
        ont = cls()

        if isinstance(json_data, str):
            json_data = json.loads(json_data)

        ont.nodes = json_data["nodes"]
        ont.relations = json_data["relations"]
        ont.raw_data = json_data

        ont.last_id = int(json_data['last_id'])

        if 'tag' in json_data:
            ont.tag = json_data['tag']

        return ont

    def to_json(self):
        self.raw_data["nodes"] = self.nodes
        self.raw_data["relations"] = self.relations
        self.raw_data["last_id"] = self.last_id

        self.raw_data["tag"] = self.tag

        if self.raw_data["tag"] == "":
            self.raw_data.pop("tag")

        return self.raw_data

    def to_json_string(self):
        return json.dumps(self.to_json(), ensure_ascii=False)

    @staticmethod
    def __elem_by_id(collection, elem_id):
        s_id = str(elem_id)
        for elem in collection:
            if elem["id"] == s_id:
                return elem
        return None

    def node_by_id(self, node_id):
        return self.__elem_by_id(self.nodes, node_id)

    def relation_by_id(self, relation_id):
        return self.__elem_by_id(self.relations, relation_id)

    def select_single_node(self, selector):
        for node in self.nodes:
            if selector(node):
                return node
        else:
            return None

    def __select_relations(self, selector):
        return [x for x in self.relations if selector(x)]

    def out_relations(self, node):
        s_id = str(node["id"])
        return self.__select_relations(
            lambda x: x["source_node_id"] == s_id)

    def in_relations(self, node):
        s_id = str(node["id"])
        return self.__select_relations(
            lambda x: x["destination_node_id"] == s_id)

    def node_by_name(self, name):
        for node in self.nodes:
            if node["name"] == name:
                return node
        return None



    def get_next_id(self):
        self.last_id += 1
        return self.last_id

    def __construct_base(self, name, attr=None):
        return {
            'id': str(self.get_next_id()),
            'attributes': attr or {},
            'namespace': self.default_namespace,
            'name': str(name),
        }

    def add_node(self, name, attr=None):
        node = self.__construct_base(name, attr)
        self.nodes.append(node)
        return node

    def add_relation(self, name, source_id, destination_id, attr=None):
        relation = self.__construct_base(name, attr)
        relation.update({
            'source_node_id': str(source_id),
            'destination_node_id': str(destination_id),
        })

        self.relations.append(relation)
        return relation

    def add_relation_by_names(self, name, source, destination, attr=None):
        return self.add_relation(
            name,
            self.node_by_name(source)['id'],
            self.node_by_name(destination)['id'], attr)
