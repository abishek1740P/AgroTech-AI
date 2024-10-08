import os
from flask import Flask, redirect, render_template, request, jsonify
from PIL import Image
import torchvision.transforms.functional as TF
import CNN
import numpy as np
import torch
import pandas as pd
from flask_cors import CORS



disease_info = pd.read_csv('disease_info.csv' , encoding='cp1252')
supplement_info = pd.read_csv('supplement_info.csv',encoding='cp1252')

model = CNN.CNN(39)    
model.load_state_dict(torch.load("plant_disease_model_1_latest.pt"))
model.eval()

def prediction(image_path):
    image = Image.open(image_path)
    image = image.resize((224, 224))
    input_data = TF.to_tensor(image)
    input_data = input_data.view((-1, 3, 224, 224))
    output = model(input_data)
    output = output.detach().numpy()
    index = np.argmax(output)
    return index



app = Flask(__name__)
application=app
# Define a route for handling HTTP GET requests to the root URL
@app.route('/', methods=['GET'])
def get_data():
    data = {
        "message":"API is Running"
    }
    return jsonify(data)
CORS(app)
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        try:
            image = request.files['image']
            filename = image.filename
            file_path = os.path.join('static/uploads', filename)
            image.save(file_path)

            pred = prediction(file_path)
            print(pred)
            if pred not in disease_info['disease_name'] or pred not in supplement_info['supplement name']:
                raise ValueError("Invalid prediction value")

            title = disease_info['disease_name'][pred]
            description = disease_info['description'][pred]
            prevent = disease_info['Possible Steps'][pred]
            image_url = disease_info['image_url'][pred]
            supplement_name = supplement_info['supplement name'][pred]
            supplement_image_url = supplement_info['supplement image'][pred]
            supplement_buy_link = supplement_info['buy link'][pred]

            # Convert any int64 to int
            if isinstance(pred, np.int64):
                pred = int(pred)

            return jsonify({
                'title': title,
                'desc': description,
                'prevent': prevent,
                'image_url': image_url,
                'pred': pred,
                'sname': supplement_name,
                'simage': supplement_image_url,
                'buy_link': supplement_buy_link
            })
        except Exception as e:
            print("error")
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

