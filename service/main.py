import os

from flask import Flask, jsonify, send_file, request, abort, Response
from flask_cors import CORS

import h5py

import numpy as np

import tensorflow.keras as keras
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from typing import List, Tuple
from PIL import Image
import base64
import io
from PIL.Image import DecompressionBombError
from sklearn.neighbors import NearestNeighbors, KNeighborsRegressor

app = Flask('image_processing_service')
cors = CORS(app)

app.debug = True
res_net = None

projects_dir = "/projects"
images_dir = "/images"
neighbours_group = 'neighbours'

project_cache = {}


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
    global project_cache

    if project in project_cache:
        (
            image_name_to_id_mapping,
            id_to_image_name_mapping,
            features_matrix
        ) = project_cache[project]
    else:
        project_data = h5py.File(f'{projects_dir}/{project}.hdf5', 'r')

        features_matrix = []
        image_name_to_id_mapping = {}
        id_to_image_name_mapping = {}

        app.logger.debug(f'Loading data for {project}...')
        for group_key in project_data:
            image_name_to_id_mapping[group_key] = len(features_matrix)
            id_to_image_name_mapping[len(features_matrix)] = group_key

            features_matrix += [project_data[group_key]['features'][()]]

        project_cache[project] = (
            image_name_to_id_mapping,
            id_to_image_name_mapping,
            features_matrix)

    app.logger.debug('Done.')

    app.logger.debug('Preprocessing uploaded image...')
    file = request.get_data()

    try:
        img = Image.open(io.BytesIO(file))
    except Exception: # TODO: More explicit except
        img = Image.open(io.BytesIO(base64.b64decode(file)))

    img = img.convert('RGB')
    img = img.resize((224, 224), Image.NEAREST)
    img = image.img_to_array(img)

    img_data = image.img_to_array(img)
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preprocess_input(img_data)
    app.logger.debug("Done.")

    app.logger.debug('Predicting nearest neighbours.')
    res_net_feature = res_net.predict(img_data)
    res_net_feature_flattened = np.array(res_net_feature).flatten()
    res_net_feature_flattened = np.expand_dims(res_net_feature_flattened, axis=0)

    nn = NearestNeighbors(n_neighbors=10)
    nn.fit(features_matrix)
    neighbours = nn.kneighbors(res_net_feature_flattened)

    neighbour_names = [id_to_image_name_mapping[i] for i in neighbours[1][0]]
    distances = [i for i in neighbours[0][0]]
    result = list(zip(neighbour_names, distances))
    app.logger.debug('Done.')
    return jsonify(result)


@app.route("/<project>/<image_name>")
def get_image_data(project, image_name):
    f = h5py.File(f'{projects_dir}/{project}.hdf5', 'r')
    file_path = f"{images_dir}/{project}/{f[image_name].attrs['path']}"
    
    if not os.path.isfile(file_path):
        abort(Response(f'Could not find image {image_name}', 404))
    return send_file(file_path)


@app.route("/<project>/features/<image_name>")
def get_image_features(project, image_name):
    f = h5py.File(f'{projects_dir}/{project}.hdf5', 'r')
    return jsonify(f[image_name]['features'][()].tolist())


@app.route("/<project>/neighbours/<image_name>/<user>")
def get_image_neighbours(project, image_name, user):

    image_list = []
    with h5py.File(f'{projects_dir}/{project}.hdf5', 'r') as f:
        if image_name not in f:
            abort(Response(f'Could not find image {image_name}', 400))
        
        for image in f[image_name][neighbours_group]:
            temp_dict = {'filename': image, 
                'distance': str(f[image_name][neighbours_group][image].attrs.get('distance'))}
            user_vote = f[image_name][neighbours_group][image].attrs.get(user)
            temp_dict['vote'] = str(user_vote) if user_vote else str(0)
            image_list.append(temp_dict)
            
    respond = jsonify(image_list)
    app.logger.debug(f'Get request for user {user} and project {project}')
    return respond


@app.route("/<project>/neighbours/<image_name>/vote", methods=['POST'])
def vote_image_for_username(project, image_name):

    try:
        username, vote, neighbour_image = read_uservote_request_body(request)
    except ValueError as ve:
        abort(Response(str(ve), 400))
    except TypeError as te:
        abort(Response(str(te), 400))

    with h5py.File(f'{projects_dir}/{project}.hdf5', 'r+') as f:
        neighbours = f[image_name].require_group(neighbours_group)
        neighbour_img = neighbours.require_group(neighbour_image)
        neighbour_img.attrs.modify(username, int(vote))

    return jsonify(message="Added vote", body=request.json)


def read_uservote_request_body(req_body) -> Tuple[str, str, str]:
    """ Read user vote request body and return data if body has valid format """
    if not req_body.is_json:
        raise TypeError('No json file provided')
    content = req_body.get_json()
    if 'vote' not in content or 'neighbour_image' not in content or 'user' not in content:
        raise ValueError('Not all data provided in request body')
    if int(content['vote']) != -1 and int(content['vote']) != 1:
        raise ValueError('Provide vote with value of either -1 or 1')
    
    return content['user'], content['vote'], content['neighbour_image']
    
def load_model():
    global res_net
    res_net = keras.applications.resnet50.ResNet50(include_top=False, pooling='avg')


if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0')
