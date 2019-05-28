import json
import argparse
import logging
import time

from sklearn.neighbors import NearestNeighbors
import numpy as np

import db.mariadb as mariadb

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(format="%(asctime)s-%(levelname)s-%(name)s - %(message)s")

parser = argparse.ArgumentParser(description="Create features for files in MariaDB.")
parser.add_argument('db_host', help="specify mariadb host.")
parser.add_argument('db_port', type=int, help="specify mariadb port.")
parser.add_argument('db_name', help="specify mariadb database.")
parser.add_argument('db_user', help="specify mariadb user.")
parser.add_argument('db_password', help="specify mariadb password.")
parser.add_argument('-n', '--nth_image', type=int, default=1,
                    help="only keep every nth image found in source directory, default: 1 (every image)")
parser.add_argument('-k', '--k_nearest', type=int, default=20,
                    help="keep k nearest neighbours for each image image, default: 20")


def create_compressed(host, port, database, user, password, n, k):
    con = mariadb.get_connection(host, port, database, user, password)
    compressed_data = mariadb.get_every_nth_file_feature(con, n)
    con.close()

    compressed_features = np.array([json.loads(data[1]) for data in compressed_data])

    logger.info('Compressed features shape: ' + str(compressed_features.shape))
    logger.info("Running KNN...")
    start_time = time.time()
    nn = NearestNeighbors(n_neighbors=k)
    compressed_neighbours = [value.tolist() for value in nn.fit(compressed_features).kneighbors()]
    logger.info(f"Done, time elapsed: {time.time() - start_time} seconds.")

    con = mariadb.get_connection(host, port, database, user, password)

    logger.info("Writing neighbours based on compressed features.")
    for idx, (image_id, _feature) in enumerate(compressed_data):

        neighbour_ids = [compressed_data[i][0] for i in compressed_neighbours[1][idx]]
        neighbour_distances = compressed_neighbours[0][idx]
        mariadb.write_neighbours(
            image_id, list(zip(neighbour_ids, neighbour_distances)), con
        )

    con.close()


def create_uncompressed(host, port, database, user, password, n, k):
    con = mariadb.get_connection(host, port, database, user, password)
    uncompressed_data = mariadb.get_every_nth_file_feature_uncompressed(con, n)
    con.close()

    uncompressed_features = np.array([json.loads(data[1]) for data in uncompressed_data])

    logger.info('Uncompressed features shape: ' + str(uncompressed_features.shape))
    logger.info("Running KNN...")
    start_time = time.time()
    nn = NearestNeighbors(n_neighbors=k)
    uncompressed_neighbours = [value.tolist() for value in nn.fit(uncompressed_features).kneighbors()]
    logger.info(f"Done, time elapsed: {time.time() - start_time} seconds.")

    con = mariadb.get_connection(host, port, database, user, password)

    logger.info("Writing neighbours based on uncompressed features.")
    for idx, (image_id, _feature) in enumerate(uncompressed_data):
        neighbour_ids = [uncompressed_data[i][0] for i in uncompressed_neighbours[1][idx]]
        neighbour_distances = uncompressed_neighbours[0][idx]

        mariadb.write_uncompressed_neighbours(
            image_id, list(zip(neighbour_ids, neighbour_distances)), con
        )

    con.close()


def start(host, port, database, user, password, n, k):
    create_compressed(host, port, database, user, password, n, k)
    create_uncompressed(host, port, database, user, password, n, k)


if __name__ == "__main__":
    options = vars(parser.parse_args())

    start(options['db_host'], options['db_port'], options['db_name'], options['db_user'],
          options['db_password'], options['nth_image'], options['k_nearest'])
