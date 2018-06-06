import sys
import pickle
import json

import numpy as np

import create_json


def group_images(data, output_directory, neighbour_count):

    counter = 1
    count = len(data)

    file_list = []

    for (file_name, features) in data:
        print(f"Evaluating neighbours for {file_name} (#{counter}/{count}).")
        counter += 1
        neighbours = []

        file_list.append(file_name)

        for(neighbour_name, neighbour_features) in data:
            if neighbour_name == file_name:
                continue

            element_wise_substraction = features - neighbour_features
            element_wise_squared = np.square(element_wise_substraction)
            summed = np.sum(element_wise_squared)
            squared_eucleadean_distance = np.sqrt(summed)

            neighbours.append((neighbour_name, squared_eucleadean_distance))

        neighbours = sorted(neighbours, key=lambda tup: tup[1])
        result = {
            'file_name': file_name,
            'neighbours': neighbours
        }

        with open(f"{output_directory}/{file_name}.neighbours.pickle", 'wb') as output_file:
            pickle.dump(result, output_file)

        create_json.write_as_json(result, output_directory, neighbour_count)

    with open(f"{output_directory}/images_list.json", 'w') as image_list_file:
        json.dump(file_list, image_list_file)


if __name__ == '__main__':
    with open(sys.argv[1], 'rb') as input_file:
        input_data = pickle.load(input_file)

        group_images(input_data, sys.argv[2], int(sys.argv[3]))
        print('Done.')
