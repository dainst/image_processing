# Image Clustering

So far, there is no clustering happening, just assigning nearest neighbours for a set of images.

## Prerequisites

* Python 3
* [Tensorflow](https://www.tensorflow.org/)
* [Docker](https://www.docker.com) and [docker compose](https://docs.docker.com/compose/), alternatively you'll need a running MySQL-/MariaDB containing the three required 
[tables](https://github.com/dainst/image_processing/tree/master/db/table_setup).
* Folder(s) with images: The script currently expects all files to have distinct names and to be JPEG.


## Running Docker

1 - Copy the docker-compose environment file template and adjust the database credentials as needed.
```
cp .env_template .env
```

2 - Build the Docker images and start one container each.
```
docker-compose build && docker-compose up
```

The [Flask](http://flask.pocoo.org/docs/1.0/) application should be accessible at [localhost:5000](localhost:5000).
It is only used to serve results. For processing images only MariaDB is required.

## Processing images

1 - Run 
```
python3 create_image_features.py <path to root image folder> <db host> <db port> <db name> <db user> <db user password>
```

The script parses all JPEG files found below `<path to root image folder>` (including subdirectories, images selected by 
suffixes).
and extracts features (a vector containing 2048 float values). The script uses TensorFlow's 
[imagenet](https://github.com/tensorflow/models/tree/master/tutorials/image/imagenet) model. Results are saved to 
in tables `image_features` and `image_names`.

2 - Run 

```
python3 group_images.py <db host> <db port> <db name> <db user> <db user password>
```
 
For each image, the script calculates the euclidean distances to all other images and then sorts the result by 
increasing distance (KNN). The first 100 nearest neighbours are stored in the MariaDB table `image_neighbours`.