from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory
from flask import url_for
from flask import redirect
from werkzeug.utils import secure_filename
import os
import subprocess
import torch
import sys
import pafy


#helper packages
import helper_predict
import helper_process_and_predict as p
import helper_generate_report as r


app = Flask(__name__, template_folder='templates', static_folder='static')

model_weights = 'model/runs/train/exp9/weights/best.pt'


upload_path = 'static/uploads/' #files/input
detections_path = 'static/output/'
youtube_videos_path = 'youtube_videos/'


@app.route('/', methods=['GET', 'POST'])
def index():
    
    return render_template("homepage.html")

@app.route('/homepage.html', methods=['GET', 'POST'])
def home():
    
    return render_template("homepage.html")


@app.route('/logo_detection.html', methods=['GET', 'POST'])
def logo_detection():
    
    return render_template("logo_detection.html")


@app.route('/upload', methods=['GET', 'POST'])
def file_upload():
    
    global filename
    global input_filename

    
    #get uploaded file
    if request.method == "POST":
        f = request.files['logofile']
        
        #check for correct file type
        if f.filename.endswith(('.png', '.jpg', '.jpeg', '.mp4')):
            # if file type is correct, save to upload_path
            f.save(os.path.join(upload_path, secure_filename(f.filename)))
            
            # get output filename
            detected_file = secure_filename(f.filename)
            filename = detected_file
            input_filename = filename
            output_filename = filename
        
    return render_template("logo_detection.html", input_filename=input_filename)


#Display input file    
@app.route('/display/<filename>')
def display_video(filename):
	#print('display_video filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + input_filename))


@app.route('/detect', methods=['GET', 'POST'])
def detect():
    
    # pass file to model for prediction
    p.process_and_predict(os.path.join(upload_path, filename))
    r.generate_report(labelmapfile='model/data/logo50.yaml', labelpath=detections_path, labelfile='label.txt')
    
    output_filename = input_filename
    done_msg = "Detection done! Thank you for using LogoSpace!"

    return render_template("logo_detection.html", done_msg=done_msg, output_filename=output_filename)


#Display output file    
@app.route('/display/<filename>')
def display_output_video(filename):
	#print('display_video filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + output_filename))


#download files
@app.route('/download', methods=['GET', 'POST'])
def download():
    
    #download output file
    try:
        return send_from_directory(directory=detections_path, path=filename)
    except Exception as e:
        return str(e)

@app.route('/download_label', methods=['GET', 'POST'])
def download_label():
    
    #download output label file
    try:
        return send_from_directory(detections_path,'label.txt', as_attachment=True)
    except Exception as e:
        return str(e)
    

@app.route('/download_report', methods=['GET', 'POST'])
def download_report():
    
    #download csv report
    try:
        return send_from_directory(detections_path,'output.csv', as_attachment=True)
    except Exception as e:
        return str(e)
   



#Youtube Video Download
@app.route("/youtube_url", methods=['GET', 'POST'])
def youtube_url():
    
    global video_stream
    
    youtube_url = request.form.get('youtube_url')
    
    video = pafy.new(youtube_url)
    video_stream = video.getbest(preftype="mp4")
    
    video_stream.download(filepath=youtube_videos_path)
    post_download = "Done! Please download the video with the Download button"
    
    return render_template("logo_detection.html", post_download=post_download)
    
@app.route("/download_youtube", methods=['GET', 'POST'])
def download_youtube():
    
    try:
        return send_from_directory(youtube_videos_path, path=video_stream.filename, as_attachment=True)
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(debug=True)
    