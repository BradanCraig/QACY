from flask import render_template, Flask, request, send_file, jsonify
from inference import *
from PIL import Image
import zipfile
import io
from tqdm import tqdm
from stats import *
import base64

app = Flask(__name__)

@app.route('/')
def main():
    return render_template("main.html")

@app.route('/infer', methods=["POST"])
def infer_images():
    imgs = request.files["images"]

    try:
        name = request.files["name"]
    except:
        name = "images"

    zip_mem = io.BytesIO()
    zipf = zipfile.ZipFile(zip_mem, "w")

    if "zip" in imgs.content_type:
        content_bytes = io.BytesIO(imgs.read())
        content = zipfile.ZipFile(content_bytes, 'r')
        
        low, mid, high = 0, 0, 0
        for img_name in tqdm(content.namelist()):
            mask = infer(Image.open(io.BytesIO(content.read(img_name))))
            results = get_percents(mask)
            
            low += results["low"]
            mid += results["mid"]
            high += results["high"]
            
            mask_b = io.BytesIO()
            mask.save(mask_b, format="PNG")
            mask_b.seek(0)
        
            zipf.writestr(img_name, mask_b.read())

        results = {
            "low": low/len(content.namelist()),
            "mid": mid/len(content.namelist()),
            "high": high/len(content.namelist())
            }

    else:
        mask=infer(img=Image.open(imgs))
        results = get_percents(mask)
        
        mask_b = io.BytesIO()
        mask.save(mask_b, format="PNG")
        mask_b.seek(0)
        
        zipf.writestr("image_0.PNG", mask_b.read())  
    
    zipf.close()
    zip_mem.seek(0)
    
    zip_data = zip_mem.read()
    zip_64 = base64.b64encode(zip_data).decode('utf-8')
    response = {
        "percents": results,
        "zip_file": zip_64,
        "name": f"{name}.zip"
    }
    
    return jsonify(response)




if __name__ == "__main__":
    app.run(port=8000, debug=True)