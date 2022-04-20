from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from werkzeug.utils import secure_filename
import os
import subprocess
import torch
import sys


#helper packages
import helper_predict
import helper_process_and_predict as p


app = Flask(__name__, template_folder='templates')


model_weights = 'model/runs/train/exp9/weights/best.pt'


upload_path = 'files/input/' #files/input
detections_path = 'files/output/'


@app.route('/', methods=['GET'])
def index():
    
    return render_template("index.html")


@app.route('/detect', methods=['POST'])
def file_upload():
    
    global download_file
    
    #get uploaded file
    if request.method == "POST":
        f = request.files['logofile']
        
        #check for correct file type
        if f.filename.endswith(('.png', '.jpg', '.jpeg', '.mp4')):
            # if file type is correct, save to upload_path
            f.save(os.path.join(upload_path, secure_filename(f.filename)))
            
            # pass file to model for prediction
            p.process_and_predict(os.path.join(upload_path, secure_filename(f.filename)))
            
            # get output filename
            detected_file = secure_filename(f.filename)
            download_file = detected_file

        
    return render_template("index.html", download_file=download_file)


@app.route('/download', methods=['GET', 'POST'])
def download():
    
    #download output file
    try:
        return send_from_directory(directory=detections_path, path=download_file)
    except Exception as e:
        return str(e)

@app.route('/download_label', methods=['GET', 'POST'])
def download_label():
    
    #download output label file
    try:
        return send_from_directory(detections_path,'label.txt', as_attachment=True)
    except Exception as e:
        return str(e)
    

if __name__ == "__main__":
    app.run(debug=True)
    