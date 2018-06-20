import sys
import os
import pickle
import json

import numpy as np


def calculate_euclidean_distance(matrix_a, matrix_b):
    # https://codereview.stackexchange.com/questions/77245/faster-solution-for-row-wise-matrix-subtraction
    d = (matrix_a ** 2).sum(axis=-1)[:, np.newaxis] + (matrix_b ** 2).sum(axis=-1)
    d -= 2 * np.squeeze(matrix_a.dot(matrix_b[..., np.newaxis]), axis=-1)
    # small negative values may appear due to rounding errors, those are set to zero
    negative_values = d < 0
    d[negative_values] = 0
    d **= 0.5
    return d


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


def _calculate_nearest_neighbours(root_path, output_directory):
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

            all_distances = None
            all_compared_images_names = []

            for inner_batch_directory in os.listdir(root_path):
                compared_images_batch_directory = f'{root_path}/{inner_batch_directory}'
                print(f'Comparing to {compared_images_batch_directory}')
                if not os.path.isdir(current_batch_directory):
                    continue

                with open(f'{compared_images_batch_directory}/image_mapping.json', 'r') as compared_images_mapping_file, \
                        open(f'{compared_images_batch_directory}/features.pickle', 'rb') as compared_images_features_file:

                    compared_images_features = np.array(pickle.load(compared_images_features_file))

                    all_compared_images_names.extend(json.load(compared_images_mapping_file))

                    if all_distances is None:
                        all_distances = calculate_euclidean_distance(
                            image_features[:, 1:],
                            compared_images_features[:, 1:]
                        )
                    else:
                        all_distances = np.append(
                            all_distances,
                            calculate_euclidean_distance(
                                image_features[:, 1:],
                                compared_images_features[:, 1:]
                            ),
                            axis=1)

            print(f'Writing batch results to disk.')

            for idx, image_name in enumerate(image_mapping):
                batch_output_path = f'{output_directory}/{batch_directory}/'
                if not os.path.exists(os.path.dirname(batch_output_path)):
                    os.makedirs(os.path.dirname(batch_output_path))

                neighbours = all_distances[idx]
                sorted_neighbour_indices = np.argsort(neighbours)
                sorted_neighbour_file_names = [all_compared_images_names[index] for index in list(sorted_neighbour_indices)]
                result = list(zip(sorted_neighbour_file_names, neighbours[sorted_neighbour_indices]))

                write_pickle(result, f'{batch_output_path}{image_name}.neighbours.pickle')
                write_json(result, f'{batch_output_path}{image_name}.neighbours.json', image_name, neighbour_count)

                file_list.append(f'{batch_output_path}{image_name}')

    with open(f'{output_directory}/images_list.json', 'w') as image_list_file:
        json.dump(file_list, image_list_file)

    print('Done.')


if __name__ == '__main__':
    _calculate_nearest_neighbours(root_path=sys.argv[1], output_directory=sys.argv[2])
