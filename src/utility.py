import json


def read_json_from_file(filename):
    '''Reads the content from a JSON file'''
    with open(filename, 'r') as json_file:
        result = json.load(json_file)
    return result


def write_json_to_file(filename, data):
    '''Writes the provided data to a JSON file'''
    with open(filename, 'w') as json_file:
        json.dump(data, json_file)
    return
