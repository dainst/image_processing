import h5py

import argparse
import logging
import numpy as np
import time
import os

from sklearn.neighbors import NearestNeighbors
from tqdm import tqdm

from global_directories import GloabalDir

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(format="%(asctime)s-%(levelname)s-%(name)s - %(message)s")

parser = argparse.ArgumentParser(description="Scan for images in the source directory.")
parser.add_argument('project', type=str, help="Specifiy project name.")
parser.add_argument('-k', '--k_nearest', type=int, default=20,
                    help="keep k nearest neighbours for each image image, default: all. If given value is all: All images from dataset are compared")


def create_neighbours(project_name: str, _k: str) -> None:
    f = h5py.File(f"{os.path.join(GloabalDir.projects,project_name)}.hdf5", 'r+')

    features_matrix = []
    image_name_to_id_mapping = {}
    id_to_image_name_mapping = {}

    for group_key in f:
        image_name_to_id_mapping[group_key] = len(features_matrix)
        id_to_image_name_mapping[len(features_matrix)] = group_key

        features_matrix += [f[group_key]['features'][()]]

    features_matrix = np.array(features_matrix)

    k = len(features_matrix) -1 if _k == 'all' else int(_k)

    logger.info(f"Features shape for project '{project_name}': {str(features_matrix.shape)}")
    logger.info("Running KNN...")
    start_time = time.time()
    nn = NearestNeighbors(n_neighbors=k)
    neighbours = [value.tolist() for value in nn.fit(features_matrix).kneighbors()]
    logger.info(f"Done, time elapsed: {time.time() - start_time} seconds.")

    logger.info("Writing result to hdf5...")
    with tqdm(total=len(f)) as pbar:
        for group_key in f:
            current_image_id = image_name_to_id_mapping[group_key]
            neighbour_names = [id_to_image_name_mapping[i] for i in neighbours[1][current_image_id]]
            neighbour_distances = neighbours[0][current_image_id]

            if 'neighbours' not in f[group_key]:
                neighbours_group = f[group_key].create_group('neighbours')
            else:
                neighbours_group = f[group_key]['neighbours']

            for idx, value in enumerate(neighbour_names):
                if value not in neighbours_group:
                    g = neighbours_group.create_group(value)
                    g.attrs['distance'] = neighbour_distances[idx]
                else:
                    neighbours_group[value].attrs['distance'] = neighbour_distances[idx]
            pbar.update(1)

    logger.info("Done")
    f.close()


if __name__ == "__main__":
    options = vars(parser.parse_args())

    create_neighbours(options['project'], options['k_nearest'])
