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
import helper_generate_report_v2 as r


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
    
    global logo_row
    global logo_col
    
    import pandas as pd
    
    trained_logo = ["Laoshan Beer", "Heineken", "Healtheries", "Bobs Red Mill", "Baskin-Robbins", "Bellamys Australia", "Yellow Tail", "BreadTalk", "Columbus", "Gudasao", "Charbonnel et Walker", "De Cecco", "Colavita", "violet crumble", "Daves Gourmet", "Huy Fong Foods", "penfolds", "Chubang", "Dr. Oetker", "Haizhilan", "tianzhilan", "Yuanshi","Master Kong", "Weidendorf", "Yanjing Beer", "Snow Beer","Meadow fresh", "Blue Bell Ice Cream", "Weidendorf", "Cholula Hot Sauce", "Taitaile", "ChangJi", "Biggby Coffee","Weidamei", "Bacardi", "Hortex", "Liubiju","BelGioioso", "evian", "Laohenghe", "Bold Rock Hard Cider","Mengzhilan", "Driscolls"]
    trained_logo_df = pd.DataFrame(trained_logo)
    trained_logo_df = trained_logo_df.rename(columns={ 0 : 'Brand Logo'})
    logo_row, logo_col = (trained_logo_df.to_dict('records'), trained_logo_df.columns.values)
    
    return render_template("logo_detection.html", logo_row=logo_row, logo_col=logo_col)


@app.route('/upload', methods=['GET', 'POST'])
def file_upload():
    
    global filename
    global input_filename
    global file_type
    
    global image_filename
    global video_filename

    #get uploaded file
    if request.method == "POST":    
        f = request.files['logofile']
            #check for correct file type
        #try:
        if f.filename.endswith(('.png', '.jpg', '.jpeg', '.mp4')):
            # if file type is correct, save to upload_path
            f.save(os.path.join(upload_path, secure_filename(f.filename)))
            
            # if f.filename.endswith(('.png', '.jpg', '.jpeg')):
            #     image_filename = secure_filename(f.filename)
            #     video_filename = False
            #     filename = image_filename
            # else:
            #     video_filename = secure_filename(f.filename)
            #     image_filename = False
                
            file_type = f.filename.split(".")
            file_type = file_type[1]
            
            # get output filename
            detected_file = secure_filename(f.filename)
            filename = detected_file
            input_filename = filename
            output_filename = filename
                
    return render_template("logo_detection.html", logo_row=logo_row, logo_col=logo_col, file_type=file_type, input_filename=input_filename)

        #except Exception as e:
         #   return str("Incorrect file type, please upload a PNG, JPG, JPEG, or MP4 file.")
        
        

#Display input file    
@app.route('/display/<filename>')
def display_video(filename):
	#print('display_video filename: ' + filename)
    
    return redirect(url_for('static', filename='uploads/' + input_filename))



@app.route('/detect', methods=['GET', 'POST'])
def detect():
    
    try:
        # pass file to model for prediction
        p.process_and_predict(os.path.join(upload_path, filename))
        records, colnames = r.generate_report(labelmapfile='model/data/logo50.yaml', labelpath=detections_path, labelfile='label.txt')
        
        output_filename = input_filename
        done_msg = "Detection done! Thank you for using LogoSpace!"
    except Exception as e:
        return str("Sorry, LogoSpace could not detect a logo, please upload a different file.")

    return render_template("logo_detection.html", done_msg=done_msg, file_type=file_type, output_filename=output_filename, records=records, colnames=colnames, logo_row=logo_row, logo_col=logo_col)


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
        return str("Sorry, there's no output file to download.")

@app.route('/download_label', methods=['GET', 'POST'])
def download_label():
    
    #download output label file
    try:
        return send_from_directory(detections_path,'label.txt', as_attachment=True)
    except Exception as e:
        return str("Sorry, there's no output label to download.")
    

@app.route('/download_report', methods=['GET', 'POST'])
def download_report():
    
    #download csv report
    try:
        return send_from_directory(detections_path,'output.csv', as_attachment=True)
    except Exception as e:
        return str("Sorry, there's no output table to download.")
   



#Youtube Video Download
@app.route("/youtube_url", methods=['GET', 'POST'])
def youtube_url():
    
    global video_stream
    
    try:   
   
        youtube_url = request.form.get('youtube_url')
        
        video = pafy.new(youtube_url)
        video_stream = video.getbest(preftype="mp4")
        
        video_stream.download(filepath=youtube_videos_path)
        post_download = "Download Ready! Please click Download Youtube Video to download"
        
        return render_template("logo_detection.html", post_download=post_download, logo_row=logo_row, logo_col=logo_col)
    except Exception as e:
        return str("Sorry, that youtube video cannot be downloaded, please try another video.")
    
@app.route("/download_youtube", methods=['GET', 'POST'])
def download_youtube():
    
    try:
        return send_from_directory(youtube_videos_path, path=video_stream.filename, as_attachment=True)
    except Exception as e:
        return str("Sorry, there's no youtube video to download. Please click 'Start Download' and wait for the success message and try again.")


if __name__ == "__main__":
    app.run(debug=True)
    