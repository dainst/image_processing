import os

from flask import Flask, jsonify, send_file
from flask_cors import CORS

import h5py
import numpy

app = Flask('image_processing_service')
cors = CORS(app, resources={r'*': {'origins': ['http://localhost*', 'http://virginiaplain08.klassarchaeologie.uni-koeln.de*']}})

app.debug = True

projects_dir = "/projects"
images_dir = "/images"


@app.route('/')
def index():

    available_projects = []
    for root, dirs, files in os.walk(projects_dir):
        for file in files:
            if file.endswith(".hdf5"):
                available_projects.append(file[:-5])
                break

    return jsonify(available_projects)


@app.route("/<project>")
def get_image_names(project):
    f = h5py.File(f'{projects_dir}/{project}.hdf5', 'r')
    return jsonify(list(f.keys()))


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


if __name__ == '__main__':
    app.run(host='0.0.0.0')
