from flask import Flask, render_template, request
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import json

app = Flask(__name__)

# Upload folder
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load model
model = tf.keras.models.load_model("butterfly_model.h5")

# Load class names
with open("class_names.json", "r") as f:
    class_names = json.load(f)


# Image preprocessing function
def preprocess_image(image_path):

    img = Image.open(image_path).convert("RGB")

    img = img.resize((224, 224))   # MUST match training

    img_array = np.array(img)

    img_array = img_array / 255.0

    img_array = np.expand_dims(img_array, axis=0)

    img_array = img_array.astype(np.float32)

    return img_array


@app.route("/", methods=["GET", "POST"])
def index():

    prediction = None
    image_path = None

    if request.method == "POST":

        file = request.files["image"]

        if file:

            filepath = os.path.join(
                app.config['UPLOAD_FOLDER'],
                file.filename
            )

            file.save(filepath)

            image = preprocess_image(filepath)

            pred = model.predict(image)

            predicted_class = class_names[np.argmax(pred)]

            confidence = round(
                np.max(pred) * 100,
                2
            )

            prediction = f"{predicted_class} ({confidence}%)"

            image_path = filepath

    return render_template(
        "index.html",
        prediction=prediction,
        image_path=image_path
    )


if __name__ == "__main__":
    app.run(debug=True)