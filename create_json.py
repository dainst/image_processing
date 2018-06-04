import sys
import pickle
import os
import json


def write_as_json(data, output_folder, neighbour_count):
    print(f"Writing {data['file_name']}'s first {neighbour_count} neighbours to JSON.")

    result = {
        'file_name': data['file_name'],
        'neighbours': []
    }
    for name, distance in data['neighbours'][0:neighbour_count]:
        result['neighbours'].append({
            'file_name': name,
            'distances': float(distance)
        })

    with open(f'{output_folder}/{result["file_name"]}.neighbours.json', 'w') as output_file:
        json.dump(result, output_file)


if __name__ == '__main__':
    input_path = sys.argv[1]
    for file in os.listdir(input_path):
        if file.endswith('.neighbours.pickle'):
            with open(f'{input_path}/{file}', 'rb') as input_file:
                write_as_json(pickle.load(input_file), sys.argv[2], int(sys.argv[3]))
