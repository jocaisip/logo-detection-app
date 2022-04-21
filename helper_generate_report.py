import os
import pandas as pd
import yaml

def generate_report(labelmapfile,
                    labelpath, labelfile, video_sec_thres=0.2):
    
    videofileformats = ['mp4']
    imagefileformats = ['png','jpg','jpeg']    
    mode='u'
    
    if not os.path.isdir(labelpath):
        print(f'{labelpath} does not exists.')
        return -1
        
    if not os.path.isfile(labelmapfile):
        print(f'{labelmapfile} file not found.')
        return -1
    
    files = [file for file in os.listdir(labelpath) if not file.endswith('.txt')]
    if len(files)!=1:
        if len(files)>1:
            print('Error. Multiple files found!')
            return -1
        else:
            print(f'Error. No file found in {labelpath}.')
            return -1
    else:
        fileext = files[0][-files[0][::-1].find('.'):]
        if fileext in imagefileformats:
            mode='i'
        elif fileext in videofileformats:
            mode='v'
        else:
            print('Error. No image/video file found.')
            return -1

    if not os.path.isfile(os.path.join(labelpath,labelfile)):
        print(f'{labelfile} file not found in {os.path.join(labelpath,labelfile)}.')
        return -1

    labelmap = {}
    with open(labelmapfile, "r") as stream:
        try:
            labelmap = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print('Cannot read labelmap.yaml file')
            print(exc)
            return -1

    df = pd.read_csv(os.path.join(labelpath,labelfile),sep=' ',header=None)
    df.columns = ['f_name','class','bb_t_x','bb_t_y','bb_b_x','bb_b_y']
    df['class_name']=df['class'].apply(lambda x:labelmap['names'][x])

    if mode=='v':
        data = df.drop([f for f in df.columns if f not in ['f_name','class_name']],axis=1).groupby(['class_name'],as_index=False).agg({"f_name":"nunique"})
        data.columns = data.columns[:-1].tolist()+['nof_frames']
        
        import cv2
        cap = cv2.VideoCapture(os.path.join(labelpath,files[0]))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))    
        data['%_of_duration']=data.nof_frames.apply(lambda x:round((x/frame_count)*100,2))
        data['duration(secs)']=data.nof_frames.apply(lambda x:round(x/fps,1))
        data_out = data[data['duration(secs)']>video_sec_thres].sort_values('nof_frames').reset_index(drop=True)
        data_out.to_csv(os.path.join(labelpath,'output.csv'),index=False)
        with open(os.path.join(labelpath,'output.json'),'w') as f:
            f.write(data_out.to_json(orient='index'))
        return data_out
    else:
        data = df.drop([f for f in df.columns if f not in ['class_name']],axis=1).groupby(['class_name'],as_index=False).size()
        data.columns = ['class_name','nof_bbox']
        data_out = data.sort_values('nof_bbox').reset_index(drop=True)
        data_out.to_csv(os.path.join(labelpath,'output.csv'),index=False)
        with open(os.path.join(labelpath,'output.json'),'w') as f:
            f.write(data_out.to_json(orient='index'))
        return data_out
    
