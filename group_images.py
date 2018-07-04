import numpy as np

import db.mariadb as mariadb

BATCH_SIZE = 50


def calculate_euclidean_distance(matrix_a, matrix_b):
    # https://codereview.stackexchange.com/questions/77245/faster-solution-for-row-wise-matrix-subtraction
    d = (matrix_a ** 2).sum(axis=-1)[:, np.newaxis] + (matrix_b ** 2).sum(axis=-1)
    d -= 2 * np.squeeze(matrix_a.dot(matrix_b[..., np.newaxis]), axis=-1)
    # small negative values may appear due to rounding errors, those are set to zero
    negative_values = d < 0
    d[negative_values] = 0
    d **= 0.5
    return d


def start():
    overall_features = mariadb.get_feature_count()

    offset = 0
    while offset < overall_features:

        offset_comparing = 0
        current_ids, current_features = mariadb.get_feature_batch(offset, BATCH_SIZE)

        current_distances = None
        current_compared_ids = []

        while offset_comparing < overall_features:
            compared_ids, compared_features = mariadb.get_feature_batch(offset_comparing, BATCH_SIZE)
            current_compared_ids.extend(compared_ids)
            if current_distances is None:
                current_distances = calculate_euclidean_distance(
                    current_features,
                    compared_features
                )
            else:
                current_distances = np.append(
                    current_distances,
                    calculate_euclidean_distance(
                        current_features,
                        compared_features
                    ),
                    axis=1)

            offset_comparing += BATCH_SIZE

        for idx, image_id in enumerate(current_ids):
            neighbour_distances = current_distances[idx]
            sorted_neighbour_indices = list(np.argsort(neighbour_distances))
            sorted_neighbour_file_names = [current_compared_ids[index] for index in sorted_neighbour_indices]
            result = list(zip(sorted_neighbour_file_names, current_distances[sorted_neighbour_indices].flatten().tolist()))

            mariadb.write_neighbours(image_id, result)
        offset += BATCH_SIZE


if __name__ == '__main__':
    mariadb.establish_connection()
    start()
