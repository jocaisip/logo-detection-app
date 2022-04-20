import os, glob, shutil
import helper_predict

def process_and_predict(path):
    out_path = r'.\files\output'
    out_dirname = 'model_output'
    
    #Deleting existing files if any
    shutil.rmtree(out_path,ignore_errors=True)
    
    #Predicting step
    helper_predict.predict(path_to_images=path,\
                           output_parent_dir=out_path,\
                           output_dirname=out_dirname)
    
    #Moving \output\model_output\*.* to \output\
    for file in os.listdir(os.path.join(out_path,out_dirname)):
        if os.path.isfile(os.path.join(out_path,out_dirname,file)):
            shutil.move(os.path.join(out_path,out_dirname,file), os.path.join(out_path,file))
    
    #Copying all \output\model_output\labels\*.txt and writing to single \output\labels.txt
    dirname = os.listdir(os.path.join(out_path,out_dirname))[0]
    with open(os.path.join(out_path,'label.txt'), 'w') as outfile:
        for file in os.listdir(os.path.join(out_path,out_dirname,dirname)):
            with open(os.path.join(out_path,out_dirname,dirname,file)) as infile:
                outfile.write(infile.read())
    
    #Deleting residual files if any
    shutil.rmtree(os.path.join(out_path,out_dirname),ignore_errors=True)