/**
 *
 * Импортирует онтологию из JSON из ont файла и возвращает объект для данных визуализации в vis.js
 *
 * Требуется предварительно подключить visjs, чтобы класс DataSet был уже подключен.
 *
 * @param {String} ontJSON - JSON ont файла
 * @returns {Object} Объект с двумя полями, nodes и edges типа DataSet,
 * который далее можно использовать в network.setData(data),
 * где network - это объект визуализации сети в vis.js
 *
 * by Sha-Grisha
 */
function importFromOnt(ontJSON) {
    var Ontology;
    try {
        Ontology = JSON.parse(ontJSON);
    } catch (e) {
        throw new Error("Invalid JSON. Parsing failed");
    }

    var result = {
        nodes: new vis.DataSet(),
        edges: new vis.DataSet()
    };

    for (var nodeI in Ontology.nodes) {
        var node = Ontology.nodes[nodeI];

        if (node.attributes.image_url !== undefined) {
            result.nodes.add({
                id: node.id,
                shape: 'circularImage', image: node.attributes.image_url
            });
        } else {
            result.nodes.add({
                id: node.id,
                label: node.name,
            });
        }

    }

    for (var edgeI in Ontology.relations) {
        var edge = Ontology.relations[edgeI];
        result.edges.add({
            to: edge.destination_node_id,
            from: edge.source_node_id,
            label: edge.name,
            arrows: 'to'
        });
    }

    return result;
}

function initializeOntology(container, ontology) {
    if (typeof container === 'string') {
        container = document.getElementById(container);
    }

    if (container === undefined) throw new Error("Element not found");

    // provide the data in the vis format
    var data = importFromOnt(ontology);
    var options = {
        layout:{
            randomSeed: 42
        }
    };

    // initialize your network!
    var network = new vis.Network(container, data, options);

    network.once("stabilizationIterationsDone", function () {
        network.setOptions({physics: false});
    });

    return {
        network: network,
        data: data
    }
}