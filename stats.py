import torch
from PIL import Image
import numpy as np




def get_percents(img: Image):
    img = np.array(img).reshape(-1,3)

    low_arr = np.count_nonzero(img ==[255,0,0])
    mid_arr = np.count_nonzero(img ==[0,0,255])
    high_arr = np.count_nonzero(img ==[0,255,0])
    
    total =  (low_arr + mid_arr + high_arr)
    return {"low": low_arr/total, "mid": mid_arr/total, "high": high_arr/total}
    
