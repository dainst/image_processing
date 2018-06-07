# Image Clustering

So far, there is no clustering happening, just assigning nearest neighbours for a set of images.

## Prerequisites

* Python 3
* [Tensorflow](https://www.tensorflow.org/)
* Folder(s) with images: The script currently expects all files to have distinct names.

## Running the scripts

1) Run `python3 create_image_features.py <path to root image folder> <path where the feature list should be saved>`. 
This creates a *pickled* list of image names and their features (=vector containing 2048 float values) as evaluated by 
the tensorflow model located at `/model`.
2) Run `python3 group_images.py <path to feature pickle, as created by previous script> <output directory> 
<neighbour count for JSON output>`. For each image, the script calculates the squared euclidean distances 
to all other images and then sorts the result by increasing distance. This sorted neighbour list is exported in two 
variants: The complete list ist *pickled* and stored as `<image_name>.neighbours.pickle`, while a JSON variant is stored
as `<image_name>.neighbours.json`. The JSON does not contain all neighbours, but only the first `k` nearest neighbours
as specified in the script argument.