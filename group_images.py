import numpy as np
import logging
import gc
import sys

import db.mariadb as mariadb

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(name)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BATCH_SIZE = 1000
NEIGHBOUR_COUNT = 100


def calculate_euclidean_distance(matrix_a, matrix_b):
    # https://codereview.stackexchange.com/questions/77245/faster-solution-for-row-wise-matrix-subtraction
    d = (matrix_a ** 2).sum(axis=-1)[:, np.newaxis] + (matrix_b ** 2).sum(axis=-1)
    d -= 2 * np.squeeze(matrix_a.dot(matrix_b[..., np.newaxis]), axis=-1)
    # small negative values may appear due to rounding errors, those are set to zero
    negative_values = d < 0
    d[negative_values] = 0
    d **= 0.5
    return d


def start(connection):
    overall_features = mariadb.get_feature_count(connection)

    offset = 0
    while offset < overall_features:

        if offset % 1000 == 0:
            logger.info(f'Processed {offset} of {overall_features}.')

        offset_comparing = 0
        current_ids, current_features = mariadb.get_feature_batch(offset, BATCH_SIZE, connection)

        current_distances = None
        current_compared_ids = []

        while offset_comparing < overall_features:
            compared_ids, compared_features = mariadb.get_feature_batch(offset_comparing, BATCH_SIZE, connection)
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

        logger.info(f'Writing results for images {offset} to {offset + BATCH_SIZE}.')
        for idx, image_id in enumerate(current_ids):
            neighbour_distances = current_distances[idx]
            sorted_neighbour_indices = list(np.argsort(neighbour_distances))[0:NEIGHBOUR_COUNT]
            sorted_neighbour_file_names = [current_compared_ids[index] for index in sorted_neighbour_indices]
            result = list(zip(sorted_neighbour_file_names, current_distances[idx][sorted_neighbour_indices].flatten().tolist()))
            mariadb.write_neighbours(image_id, result, connection)

        current_distances = None
        sorted_neighbour_indices = None
        sorted_neighbour_file_names = None
        result = None

        logger.info('Forcing garbage collection.')
        gc.collect()

        offset += BATCH_SIZE


if __name__ == '__main__':

    if len(sys.argv) != 6:
        logger.info('Please provide as arguments: ')
        logger.info(' 1) MariaDB host.')
        logger.info(' 2) MariaDB port.')
        logger.info(' 3) MariaDB database name.')
        logger.info(' 4) MariaDB user.')
        logger.info(' 5) MariaDB password.')

    connection = mariadb.get_connection(
        host=sys.argv[1],
        port=int(sys.argv[2]),
        db_name=sys.argv[3],
        user=sys.argv[4],
        password=sys.argv[5]
    )
    start(connection)
    connection.close()
