import json
import sys
import networkx as nx
from networkx.readwrite import json_graph
import matplotlib.pyplot as plt


def usage():
    print('Usage: python3 transform.py <input.json>')
    exit()

node_map = {}
    
def transform(data):
    # filter entries with insufficient data
    data = clean(data)
    build_node_map(data)

    # build graph
    graph = build_graph(data)

    # calc scores
    scores = nx.pagerank(graph)

    # build graph json
    return build_graph_json(data, scores)


def clean(data):
    filtered = list(filter(filter_item, data))
    for item in filtered:
        item['influences'] = list(filter(filter_item, item['influences']))
        item['influenced'] = list(filter(filter_item, item['influenced']))
    return filtered


def build_node_map(data):
    for item in data:
        pageid = item['pageid']
        node_map[int(pageid)] = item


def filter_item(item):
    return item['name'] is not None and item['pageid'] is not None


def build_graph(data):
    graph = nx.DiGraph()
    for item in data:
        graph.add_node(int(item['pageid']))

    for item in data:
        for influence in item['influences']:
            if int(influence['pageid']) in node_map:
                graph.add_edge(int(item['pageid']), int(influence['pageid']))

    return graph


def build_graph_json(data, scores):
    graph_json = {'nodes': [], 'links': []}
    for pageid, score in scores.items():
        node_map[pageid]['score'] = score
    
    for item in data:
        graph_json_item = {'id': item['pageid'], 'score': item['score']}
        graph_json['nodes'].append(graph_json_item)
        for influence in item['influences']:
            if int(influence['pageid']) in node_map:
                graph_json_edge = {'source': item['pageid'], 'target': influence['pageid'], 'value': 1}
                graph_json['links'].append(graph_json_edge)

    return graph_json


if len(sys.argv) < 2:
    usage()

with open(sys.argv[1], "r") as input_file:
    data = json.load(input_file)
    transformed = transform(data)
    with open("transformed.json", "w") as output_file:
        json.dump(transformed, output_file)