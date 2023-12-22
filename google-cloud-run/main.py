#Kode ini mengatur konfigurasi lingkungan TensorFlow pada tingkat log, dengan tujuan mengurangi jumlah pesan peringatan yang ditampilkan
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import sys

#Import yang diperluin sama Python untuk keperluan pengolahan gambar dan pengembangan model machine learning dengan TensorFlow
import io
import tensorflow as tf
from tensorflow import keras
import numpy as np
from PIL import Image

# Flask membantu kita menentukan bagaimana aplikasi kita harus menanggapi berbagai jenis permintaan ini. Misalnya, jika seseorang membuka halaman utama situs kita, Flask dapat memberikan halaman selamat datang
from flask import Flask, request, jsonify


# Firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use a service account.
cred = credentials.Certificate('deploy-ml-test-nyoman-firebase-adminsdk-sdwod-163b6237db.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# fungsi dari Keras yang digunakan untuk memuat model dari file dengan ekstensi .h5. Model neural network yang telah disimpan sebelumnya dalam format HDF5 dapat dimuat kembali ke dalam variabel model.
model = keras.models.load_model("nn.h5")

# Untuk debugging, yang nantinya jika ada error,warning, dll akan muncul di console
import logging
logging.basicConfig(level=logging.DEBUG)

# Menerima objek gambar dari Pillow (PIL) dan melakukan transformasi tertentu untuk mempersiapkannya sebagai input untuk model neural network 
def transform_image(pillow_image):
    # Mengubah gambar Pillow menjadi array NumPy
    data = np.asarray(pillow_image)
    # Normalisasi nilai piksel ke dalam rentang [0, 1]
    data = data / 255.0
     # Menambahkan dimensi tambahan untuk batch dan channel
    data = data[np.newaxis, ..., np.newaxis]x
    # --> [1, x, y, 1]SS
    # Menyesuaikan ukuran gambar menjadi [28, 28]
    data = tf.image.resize(data, [28, 28])
    return data

def predict(x):
    predictions = model(x)
    predictions = tf.nn.softmax(predictions)
    pred0 = predictions[0]
    label0 = np.argmax(pred0)
    return label0

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get('file')
        print(file, flush=True)
        app.logger.info('Processing default request')
        # return jsonify({"error": file})
        if file is None or file.filename == "":
            return jsonify({"error": "no file test test"})
        try:
            image_bytes = file.read()
            pillow_img = Image.open(io.BytesIO(image_bytes)).convert('L')
            tensor = transform_image(pillow_img)
            prediction = predict(tensor)
            print(prediction, flush=True)
            # Untuk menampilkan rekomendasi ikan
            # query = db.collection('angka').where("Document ID", '==', int(prediction))
            # results = query.stream()

            # print("result >>>>>>>>>>>>>>>>>>> " + jsonify(results), flush=True)
            # Example: Query all documents in the 'fish_info' collection
            collection_ref = db.collection('angka')
            documents = collection_ref.stream()

            for doc in documents:
                # Properly consume both document ID and data
                if int(prediction) == int(doc.id):
                    penjelasan = doc.to_dict()
                    print(f'Data: {doc.to_dict()}')
                    break
            data = {"prediction": int(prediction), "penjelasan" : penjelasan}
            return jsonify(data)
        except Exception as e:
            return jsonify({"error": str(e)})
        

    # for doc in results:
    #     print(f'Document ID: {doc.id}')
    #     print(f'Data: {doc.to_dict()}')

         

    return "OK"


if __name__ == "__main__":
    app.run(debug=True)