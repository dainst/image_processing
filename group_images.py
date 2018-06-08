import sys
import os
import pickle
import json

import numpy as np


def calculate_euclidean_destances(input_vector, feature_matrix):
    element_wise_substraction = input_vector - feature_matrix
    element_wise_squared = np.square(element_wise_substraction)
    summed = np.sum(element_wise_squared, axis=1)
    squared_eucleadean_distance = np.sqrt(summed)

    return squared_eucleadean_distance


def write_json(neighbours, output_path, file_name, neighbour_count):

    result = {
        'file_name': file_name,
        'neighbours': []
    }
    for name, distance in neighbours[0:neighbour_count]:
        result['neighbours'].append({
            'file_name': name,
            'distances': float(distance)
        })

    with open(output_path, 'w') as output_file:
        json.dump(result, output_file)


def write_pickle(neighbours, output_path):
    with open(output_path, 'wb') as output_file:
        pickle.dump(neighbours, output_file)


def find_neighbours(root_path, image_name, feature, batch_number):
    input_image_index = feature[0]
    input_features = feature[1:]

    result = []

    for directory in os.listdir(root_path):
        current_batch_folder = f'{root_path}/{directory}'
        if not os.path.isdir(current_batch_folder):
            continue

        with open(f'{current_batch_folder}/image_mapping.json', 'r') as image_mapping_file, \
                open(f'{current_batch_folder}/features.pickle', 'rb') as image_features_file:
            data = pickle.load(image_features_file)

            image_mapping = json.load(image_mapping_file)

            features = data[:, 1:]

            batch_distances = calculate_euclidean_destances(input_features, features)

            counter = 0
            while counter < len(image_mapping):
                result.append((image_mapping[counter], batch_distances[counter]))
                counter += 1

    result = sorted(result, key=lambda tup: tup[1])

    return result


if __name__ == '__main__':

    root_path = sys.argv[1]
    output_directory = sys.argv[2]
    neighbour_count = 20
    file_list = []

    for batch_directory in os.listdir(root_path):
        current_batch_directory = f'{root_path}/{batch_directory}'
        if not os.path.isdir(current_batch_directory):
            continue

        print(f'Processing directory {current_batch_directory}.')

        with open(f'{current_batch_directory}/image_mapping.json', 'r') as image_mapping_file, \
                open(f'{current_batch_directory}/features.pickle', 'rb') as image_features_file:

            image_mapping = json.load(image_mapping_file)
            image_features = np.array(pickle.load(image_features_file))

            counter = 0

            while counter < image_features.shape[0]:
                image_name = image_mapping[counter]

                neighbours = find_neighbours(root_path,
                                             image_name,
                                             image_features[counter],
                                             int(batch_directory))

                batch_output_path = f'{output_directory}/{batch_directory}/'
                if not os.path.exists(os.path.dirname(batch_output_path)):
                    os.makedirs(os.path.dirname(batch_output_path))

                write_pickle(neighbours, f'{batch_output_path}{image_name}.neighbours.pickle')
                write_json(neighbours, f'{batch_output_path}{image_name}.neighbours.json', image_name, neighbour_count)

                file_list.append(f'{batch_output_path}{image_name}')

                counter += 1

        break

    with open(f'{output_directory}/images_list.json', 'w') as image_list_file:
        json.dump(file_list, image_list_file)

    print('Done.')
