from model import MaskModel
import torch
from torchvision import transforms
import torchvision
import ast





def infer(img):
    model = MaskModel(inputChannels=3, outputChannels=4, sizes=[16, 32, 64, 128, 256, 512, 1024])

    if torch.cuda.is_available():
        model.load_state_dict(torch.load("static/MaskModel_100_Epochs_Fixed_Data_V2", map_location=torch.device('cuda')))

    else:
        model.load_state_dict(torch.load("static/MaskModel_100_Epochs_Fixed_Data_V2", map_location=torch.device('cpu')))
    
    tran = transforms.Compose([transforms.Resize((2048, 2048)), transforms.ToTensor()])

    img = tran(img)
    img = torch.unsqueeze(img, dim=0)
    preds = model(img)

    preds = torch.nn.functional.softmax(preds, dim = 1)#logits to preds
    labels = torch.argmax(preds, dim=1)
    
    return decode_img(
        img=labels,
        img_h=2048,
        img_w=2048, 
        colormap= {
        
        '[0, 0, 0]': 0,
        '[255, 0, 0]': 1,
        '[0, 0, 255]': 2,
        '[0, 255, 0]': 3 
    
    })



def decode_img(img, img_h, img_w, colormap):
        reverse_colormap = {v: k for k, v in colormap.items()}

        # Apply the reverse colormap to convert integers to RGB values
        # Using list comprehension to map each label
        flattened_labels = img.flatten()
        labels_rgb_flatten = ([reverse_colormap[label.item()] for label in flattened_labels])
        
        labels_rgb_flatten= [ast.literal_eval(x) for x in labels_rgb_flatten]

        labels_rgb = torch.tensor(labels_rgb_flatten).reshape((img_h, img_w, 3))
        labels_rgb = labels_rgb.permute(2, 1, 0)

        labels_rgb = transforms.Resize((img_h, img_w))(labels_rgb)
        labels_rgb = transforms.RandomHorizontalFlip(p=1)(labels_rgb)
        labels_rgb = torchvision.transforms.functional.rotate(img=labels_rgb, angle=90, interpolation=torchvision.transforms.InterpolationMode.NEAREST)
        labels_rgb = transforms.ToPILImage()(labels_rgb.byte())
        return labels_rgb