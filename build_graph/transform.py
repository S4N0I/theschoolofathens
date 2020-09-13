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
    filtered = list(filter(filter_with_born_bound, data))
    for item in filtered:
        item['influences'] = list(filter(filter_item, item['influences']))
        item['influenced'] = list(filter(filter_item, item['influenced']))
        handle_born_corner_cases(item)
        handle_name_corner_cases(item)
    return filtered


def handle_born_corner_cases(item):
    if 'Mikhail Bakhtin' in item['name']:
        item['born'] = -2366755200
    if 'Adolf von Harnack' in item['name']:
        item['born'] = -3755289600
    if 'Nicolai Hartmann' in item['name']:
        item['born'] = -2776982400
    if 'Richard Hooker' in item['name']:
        item['born'] = -13127702400
    if 'David Hume' in item['name']:
        item['born'] = -8173267200
    if 'Hermann Graf von Keyserling' in item['name']:
        item['born'] = -2840140800
    if 'Salomon Maimon' in item['name']:
        item['born'] = -6847804800
    if 'Maimonides' in item['name']:
        item['born'] = -26350099200
    if 'Wilhelm Ostwald' in item['name']:
        item['born'] = -3692131200
    if 'Ioane Petritsi' in item['name']:
        item['born'] = -30610224000
    if 'Petar II Petrović-Njegoš' in item['name']:
        item['born'] = -4954435200
    if 'Joseph Priestley' in item['name']:
        item['born'] = -7478956800
    if 'Vasily Rozanov' in item['name']:
        item['born'] = -3597523200
    if 'Adam Smith' in item['name']:
        item['born'] = -7794576000
    if 'Frederick Robert Tennant' in item['name']:
        item['born'] = -3281904000
    if 'Udayana' in item['name']:
        item['born'] = -33765897600

def handle_name_corner_cases(item):
    if item['pageid'] == '1254755':
        item['name'] = 'Abdolkarim Soroush'
    if item['pageid'] == '16340':
        item['name'] = 'Jean-Paul Sartre'
    if item['pageid'] == '251240':
        item['name'] = 'Emil Cioran'
    if item['pageid'] == '59041318':
        item['name'] = 'August Wilhelm Rehberg'


def build_node_map(data):
    for item in data:
        pageid = item['pageid']
        node_map[int(pageid)] = item


def filter_item(item):
    return item['name'] is not None and item['pageid'] is not None

def filter_with_born_bound(item):
    return filter_item(item) and item['born'] is not None and item['born'] >= -1000000000000


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
        graph_json_item = {'id': item['pageid'], 'score': item['score'], 'name': item['name'], 'born': item['born'], 'img': item['img']}
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
    with open("transformed.js", "w") as output_file:
        output_file.write('var graph = ')
        json.dump(transformed, output_file)