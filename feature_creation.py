# RUN AUTOENCODER JUPYTER NOTEBOOK FIRST, this will create the `encoder.h5` file used below

import keras
from keras.models import load_model

from keras.models import Model
from keras.preprocessing import image
from keras.applications.resnet50 import preprocess_input
from PIL.Image import DecompressionBombError
import db.mariadb as mariadb
import numpy as np

print("Loading models...")

res_net = keras.applications.resnet50.ResNet50(include_top=False, pooling='avg')

encoder = load_model('model/encoder.h5')

print("Combining models...")
combined = Model(inputs=res_net.input, outputs=encoder(res_net.output))

con = mariadb.get_connection("127.0.0.1", 3308, "image_processing", "user", "user_pw")

files_batch = mariadb.get_all_files_data(con)

features = []
features_info = []

# Create training and test features
print("Creating image features using both models.")
counter = 1

for (img_id, name, path, url) in files_batch:
    try:
        if counter % 100 == 0:
            print(f'Progress: {counter}/{len(files_batch)}')

        img = image.load_img(path, target_size=(224, 224))
        img_data = image.img_to_array(img)
        img_data = np.expand_dims(img_data, axis=0)
        img_data = preprocess_input(img_data)

        combined_feature = combined.predict(img_data)
        combined_feature = np.array(combined_feature).flatten()

        res_net_feature = res_net.predict(img_data)
        res_net_feature = np.array(res_net_feature).flatten()

        mariadb.write_file_features(img_id, combined_feature, con)
        mariadb.write_uncompressed_file_features(img_id, res_net_feature, con)

        counter += 1

    except OSError as e:
        print(e)
    except DecompressionBombError as e:
        print(e)
        print(path)

con.close()
print('Done.')
