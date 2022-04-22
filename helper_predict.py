from model import utils
from model import detect
display = utils.notebook_init()  # checks

def predict(path_to_images='model/data/images', path_to_weights='model/runs/train/exp9/weights/best.pt',
            output_parent_dir='model/runs/detect',output_dirname='exp',conf_score=0.30):
        
        detect.run(weights=path_to_weights, source=path_to_images,
                   project=output_parent_dir, name=output_dirname, conf_thres=conf_score)

if __name__ == "__main__":
    predict()