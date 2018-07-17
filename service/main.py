from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
import db.mariadb as mariadb

app = Flask('nlp_service')
cors = CORS(app, resources={r'*': {'origins': 'http://localhost*'}})
app.debug = True


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


@app.route('/image_name_and_neighbours/<image_id>', methods=['GET'])
def image_name_and_neighbours(image_id):
    connection = get_connection()

    app.logger.debug(f'Image {image_id} requested.')
    query_result = mariadb.get_image_and_neigbours_by_id(image_id, connection)
    connection.close()
    return jsonify(query_result)


def get_connection():
    return mariadb.get_connection(
        host='image_processing_db',
        port=3306,
        db_name='image_processing_db',
        user='main_user',
        password='pwd'
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0')
