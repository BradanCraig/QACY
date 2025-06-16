from flask import render_template, Flask, request, send_file
from inference import *
from PIL import Image
import zipfile
import io
from tqdm import tqdm


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
        
        for img_name in tqdm(content.namelist()):
            mask = infer(Image.open(io.BytesIO(content.read(img_name))))

            mask_b = io.BytesIO()
            mask.save(mask_b, format="PNG")
            mask_b.seek(0)
        
            zipf.writestr(img_name, mask_b.read())



    else:
        mask=infer(img=Image.open(imgs))

        mask_b = io.BytesIO()
        mask.save(mask_b, format="PNG")
        mask_b.seek(0)
        
        zipf.writestr("image_0.PNG", mask_b.read())  
    
    zipf.close()
    zip_mem.seek(0)
    return send_file(zip_mem, download_name=f"{name}.zip", as_attachment=True)





if __name__ == "__main__":
    app.run(port=8000, debug=True)