import os

from flask import Flask, jsonify, send_file, request
from flask_cors import CORS

import h5py

import numpy as np

import tensorflow.keras as keras
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from PIL import Image
import io
from PIL.Image import DecompressionBombError
from sklearn.neighbors import NearestNeighbors, KNeighborsRegressor

app = Flask('image_processing_service')
cors = CORS(app)

app.debug = True
res_net = None

projects_dir = "/projects"
images_dir = "/images"


@app.route('/')
def index():

    available_projects = []
    for root, dirs, files in os.walk(projects_dir):
        for file in files:
            if file.endswith(".hdf5"):
                available_projects.append(file[:-5])

    return jsonify(available_projects)


@app.route("/<project>")
def get_image_names(project):
    f = h5py.File(f'{projects_dir}/{project}.hdf5', 'r')
    return jsonify(list(f.keys()))


@app.route('/<project>/upload', methods=['POST'])
def upload(project):
    global res_net
    project_data = h5py.File(f'{projects_dir}/{project}.hdf5', 'r')

    features_matrix = []
    image_name_to_id_mapping = {}
    id_to_image_name_mapping = {}

    app.logger.debug(f'Loading data for {project}.')
    for group_key in project_data:
        image_name_to_id_mapping[group_key] = len(features_matrix)
        id_to_image_name_mapping[len(features_matrix)] = group_key

        features_matrix += [project_data[group_key]['features'][()]]

    app.logger.debug('Done.')

    file = request.get_data()
    app.logger.debug(type(file))
    img = Image.open(io.BytesIO(file))
    img = img.convert('RGB')
    img = img.resize((224, 224), Image.NEAREST)
    img = image.img_to_array(img)

    app.logger.debug("Loaded...")
    app.logger.debug(img.shape)

    img_data = image.img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preprocess_input(img_data)

    app.logger.debug("Preprocessed...")
    app.logger.debug(img_data.shape)

    res_net_feature = res_net.predict(img_data)
    res_net_feature_flattened = np.array(res_net_feature).flatten()
    res_net_feature_flattened = np.expand_dims(res_net_feature_flattened, axis=0)

    app.logger.debug(np.array(features_matrix).shape)
    app.logger.debug(res_net_feature_flattened.shape)

    nn = NearestNeighbors(n_neighbors=10)
    nn.fit(features_matrix)
    neighbours = nn.kneighbors(res_net_feature_flattened)

    # neighbours = [value.tolist() for value in nn.fit(features_matrix).kneighbors()]
    app.logger.debug(neighbours)

    neighbour_names = [id_to_image_name_mapping[i] for i in neighbours[1][0]]
    app.logger.debug(neighbour_names)

    return jsonify(neighbour_names)


@app.route("/<project>/<image_name>")
def get_image_data(project, image_name):
    f = h5py.File(f'{projects_dir}/{project}.hdf5', 'r')
    return send_file(f"{images_dir}/{project}/{f[image_name].attrs['path']}")


@app.route("/<project>/features/<image_name>")
def get_image_features(project, image_name):
    f = h5py.File(f'{projects_dir}/{project}.hdf5', 'r')
    return jsonify(f[image_name]['features'][()].tolist())


@app.route("/<project>/neighbours/<image_name>")
def get_image_neighbours(project, image_name):
    f = h5py.File(f'{projects_dir}/{project}.hdf5', 'r')

    result = []
    for neighbour_name in f[image_name]['neighbours']:
        result += [(
            neighbour_name, float(f[image_name]['neighbours'][neighbour_name].attrs['distance'][()])
        )]

    result = sorted(result, key=lambda tup: tup[1])
    app.logger.debug(result)

    return jsonify(result)


def load_model():
    global res_net
    res_net = keras.applications.resnet50.ResNet50(include_top=False, pooling='avg')


if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0')
