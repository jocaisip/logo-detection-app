from flask import Flask
from flask import request
from flask import render_template
from flask import Response
from flask import url_for
from werkzeug.utils import secure_filename, send_from_directory
import os
import torch
import numpy as np
import pandas as pd
import cv2



app = Flask(__name__, template_folder='templates')


# yolov5 object detection weights for prediction

model_weights = 'yolov5/runs/train/exp9/weights/best.pt'


upload_path = "uploads/"


@app.route('/', methods=['GET'])
def index():
    
    return render_template("index.html")


@app.route('/', methods=['POST'])
def file_upload():
    if request.method == "POST":
        f = request.files['logofile']
        
        if f.filename.endswith(('.png', '.jpg', '.jpeg', '.mp4')):
            f.save(os.path.join(upload_path, secure_filename(f.filename)))
    
    return render_template("index.html")
    
            
    

if __name__ == "__main__":
    app.run(debug=True)
    