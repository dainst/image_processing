import os

from flask import Flask, jsonify, make_response
from flask_cors import CORS
import json
import mimetypes
import numpy as np

from io import BytesIO
import db.mariadb as mariadb

import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

app = Flask('image_processing_service')
cors = CORS(app, resources={r'*': {'origins': ['http://localhost*', 'http://virginiaplain08.klassarchaeologie.uni-koeln.de*']}})

app.debug = True

mimetypes.add_type('image/svg+xml', '.svg')


@app.route('/')
def index():
    app.logger.debug('Hello Wolfgang! Says the debug logger...')
    return 'Hello Wolfgang!'


@app.route('/image_count', methods=['GET'])
def image_count():
    connection = get_connection()

    app.logger.debug(f'Image count requested.')
    query_result = mariadb.get_image_count(connection)
    connection.close()
    return jsonify(query_result)


@app.route('/image_name/<image_id>', methods=['GET'])
def image_name(image_id):
    connection = get_connection()

    app.logger.debug(f'Image {image_id} requested.')
    query_result = mariadb.get_image_name(image_id, connection)
    connection.close()
    return jsonify(query_result)


@app.route('/image_fingerprint/<image_id>', methods=['GET'])
def image_fingerprint(image_id):
    connection = get_connection()

    app.logger.debug(f'Image {image_id} requested.')
    query_result = mariadb.get_features_for_id(image_id, connection)
    connection.close()

    data = json.loads(query_result[1])

    reshaped = np.resize(data, 46*46)
    reshaped = np.resize(reshaped, (46, 46))

    fig = Figure()
    ax = fig.add_subplot(111)
    ax.imshow(reshaped, interpolation='nearest', cmap='plasma')
    canvas = FigureCanvas(fig)

    fig.axes[0].set_axis_off()

    img = BytesIO()
    canvas.print_figure(img, format='svg', transparent=True, bbox_inches='tight')

    response = make_response(img.getvalue())
    response.headers['Content-Type'] = 'image/svg+xml'

    return response


@app.route('/image_name_and_neighbours/<image_id>', methods=['GET'])
def image_name_and_neighbours(image_id):
    connection = get_connection()

    app.logger.debug(f'Image {image_id} requested.')
    query_result = mariadb.get_image_and_neigbours_by_id(image_id, connection)
    connection.close()
    return jsonify(query_result)


def get_connection():
    return mariadb.get_connection(
        host=os.environ['DB_HOST'],
        port=3306,
        db_name=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0')
