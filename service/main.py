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

    project_files = []
    for root, dirs, files in os.walk(projects_dir):
        app.logger.warning(os.path.abspath(root))
        for file in files:
            app.logger.warning(file)
            if file.lower().endswith(".hdf5"):
                project_files.append((file, os.path.abspath(f'{root}/{file}')))
                break

    return jsonify(project_files)


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


#
# @app.route('/image_count', methods=['GET'])
# def image_count():
#     connection = get_connection()
#
#     app.logger.debug(f'Image count requested.')
#     query_result = mariadb.get_image_count(connection)
#     connection.close()
#     return jsonify(query_result)
#
#
# @app.route('/images_with_neighbours', methods=['GET'])
# def images_with_neighbours_count():
#     connection = get_connection()
#     query_result = mariadb.get_images_with_neighbours(connection)
#     connection.close()
#
#     return jsonify({"compressed": query_result[0], "uncompressed": query_result[1]})
#
#
# @app.route('/image_fingerprint/<image_id>', methods=['GET'])
# def image_fingerprint(image_id):
#     connection = get_connection()
#
#     app.logger.debug(f'Image {image_id} requested.')
#     query_result = mariadb.get_features_for_id(image_id, connection)
#     connection.close()
#
#     data = json.loads(query_result[1])
#
#     reshaped = np.resize(data, 46*46)
#     reshaped = np.resize(reshaped, (46, 46))
#
#     fig = Figure()
#     ax = fig.add_subplot(111)
#     ax.imshow(reshaped, interpolation='nearest', cmap='plasma')
#     canvas = FigureCanvas(fig)
#
#     fig.axes[0].set_axis_off()
#
#     img = BytesIO()
#     canvas.print_figure(img, format='svg', transparent=True, bbox_inches='tight')
#
#     response = make_response(img.getvalue())
#     response.headers['Content-Type'] = 'image/svg+xml'
#
#     return response
#
#
# @app.route('/image_name_and_neighbours/<image_id>', methods=['GET'])
# def image_name_and_neighbours(image_id):
#     connection = get_connection()
#
#     app.logger.debug(f'Image {image_id} requested.')
#     query_result = mariadb.get_image_and_neigbours_by_id(image_id, connection)
#     connection.close()
#     return jsonify(query_result)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
